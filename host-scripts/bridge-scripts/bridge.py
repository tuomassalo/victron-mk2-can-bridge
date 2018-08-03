from __future__ import print_function
from datetime import datetime
import time
import json
import sys
import os
import pickle
from struct import pack
from serial import Serial

STATEFILE = '/opt/victron-dir/state.pck'
MOCK = (sys.platform == 'darwin')

if MOCK:
  from mockmk2 import MK2
  mk2_ = MK2().start()
else:
  from pyusbtin.usbtin import USBtin
  from pyusbtin.canmessage import CANMessage
  from ib.victron.scripts.options import options
  from ib.victron.mk2 import MK2
  port = Serial(options.port, options.baudrate, timeout=options.timeout)
  mk2_ = MK2(port).start()

class PowerCounter(object):
  def __init__(self):
    self.prev_moment = datetime.now()
    self.today = 0.0
    self.since_float = 0.0

  def reset_float(self):
    self.since_float = 0.0

  def add(self, power):
    moment = datetime.now()

    # Zero the counter if the date has just changed.
    if moment.date() != self.prev_moment.date():
      self.today = 0.0

    duration = (moment - self.prev_moment).total_seconds()
    self.since_float += duration * power
    self.today       += duration * power

    self.prev_moment = moment


class Bridge(object):
  def __init__(self, mk2):
    self.mk2 = mk2
    self.state = 0
    self.state_timestamp = time.time()
    self.yield_counter = PowerCounter()
    self.usage_counter = PowerCounter()

  def set_state(self, state):
    self.state = state
    self.state_timestamp = time.time()

  def add_yield(self, power):
    self.yield_counter.add(power)

  def loop(self):
    i = 0
    while True:
      i += 1
      try:
        self._iterate()
      except Exception as e:
        print(e)
      time.sleep(1)

      # Save the state every 10 seconds
      if i % 10 == 0:
        f = open(STATEFILE, 'w')
        tmp_mk2 = self.mk2
        self.mk2 = None
        pickle.dump(self, f)
        self.mk2 = tmp_mk2
        f.close()


  def _iterate(self):
    out = dict()

    ac = self.mk2.ac_info()
    dc = self.mk2.dc_info()

    out['ac_consumption'] = ac['uinv'  ] * ac['iinv'   ]
    out['ac_in'         ] = ac['umains'] * ac['imains' ]

    out['dc_charge']      = dc['ubat'  ] * dc['icharge']
    out['dc_discharge']   = dc['ubat'  ] * dc['ibat'   ]

    # For heartbeat, see docker-watchdog.sh
    print(json.dumps(dict(
      d=datetime.utcnow().isoformat() +'Z',
      t=int(time.time()),
      v=dc['ubat'],
      state_age=time.time() - self.state_timestamp,
    ), sort_keys=True))

    if self.state == 5: # float
      self.usage_counter.reset_float()
      self.yield_counter.reset_float()

    self.usage_counter.add(out['dc_discharge'])

    out['state'] = self.state
    out['usage_since_float'] = self.usage_counter.since_float
    out['usage_today'      ] = self.usage_counter.today
    out['yield_since_float'] = self.yield_counter.since_float
    out['yield_today'      ] = self.yield_counter.today

    # For debug purposes
    print(out)

    # TEST
    # can_msg = CANMessage(0x19F21424, pack("<HHHH",
    #   1,2,3,4
    # ))
    # print can_msg.to_string()
    if not MOCK:
      # === 64 bits:
      # LSB ...
      # 14 bits: (0..16383) - usage_since_float (* 2 Wh)
      # 14 bits: (0..16383) - usage_today       (* 2 Wh)
      # 14 bits: (0..16383) - yield_since_float (* 2 Wh)
      # 14 bits: (0..16383) - yield_today       (* 2 Wh)
      # 5 bits: (0..31) inverter state
      # 3 bits: unused
      # MSB
      # print(dict(CCCCCD=
      #   ((int(self.usage_counter.since_float / 3600.0 / 2.0) & (1<<14) - 1) <<      0) +
      #   ((int(self.usage_counter.today       / 3600.0 / 2.0) & (1<<14) - 1) <<     14) +
      #   ((int(self.yield_counter.since_float / 3600.0 / 2.0) & (1<<14) - 1) << 2 * 14) +
      #   ((int(self.yield_counter.today       / 3600.0 / 2.0) & (1<<14) - 1) << 3 * 14) +
      #   ((state                                              & (1<< 5) - 1) << 4 * 14)
      # ))
      can_msg2 = CANMessage(0xCCCCCD, pack("<Q",
        ((int(self.usage_counter.since_float / 3600.0 / 8.0) & (1<<14) - 1) <<      0) +
        ((int(self.usage_counter.today       / 3600.0 / 8.0) & (1<<14) - 1) <<     14) +
        ((int(self.yield_counter.since_float / 3600.0 / 8.0) & (1<<14) - 1) << 2 * 14) +
        ((int(self.yield_counter.today       / 3600.0 / 8.0) & (1<<14) - 1) << 3 * 14) +
        ((self.state                                         & (1<< 5) - 1) << 4 * 14)
      ))
      usbtin.send(can_msg2)

      can_msg = CANMessage(0xCCCCCC, pack("<HHHH",
        int(out['ac_consumption']),
        int(out['ac_in'         ]),
        int(out['dc_charge'     ]),
        int(out['dc_discharge'  ]),
      ))
      usbtin.send(can_msg)

def init_bridge():
  try:
    age = time.time() - os.stat(STATEFILE).st_mtime
    print("RESTORE file age: %d seconds" % int(age))
    if -600 < age < 600: # 10 minutes
      try:
        print("... RESTORING")
        f = open(STATEFILE)
        b = pickle.load(f)
        b.mk2 = mk2_
        f.close()
        return b
      except EOFError:
        print("RESTORE EOFError")
      except Exception as e:
        print("OTher error: %s" % e)
    else:
      print("... RESTORE file too old.")
  except OSError:
    print("RESTORE file not found")

  print("INIT bridge")
  return Bridge(mk2_)

bridge = init_bridge()

def listen_mppt(msg):

  data = msg.get_data()
  # PGN 127508
  if msg.mid == 0x19F21424 and data[0] == 0x00:
    v = (data[2] * 256 + data[1]) / 100.0
    i = (data[4] * 256 + data[3]) / 10.0
    # print(dict(v=v, i=i, w=v*i))

    bridge.add_yield(v * i)

  # PGN 127750
  elif msg.mid == 0x19F30624:
    bridge.set_state(data[2])


if MOCK:
  from random import randint
  import threading

  def mock_call_listen_mppt():

    class MockMsg1(object):
      mid = 0x19F21424
      @classmethod
      def get_data(cls):
        data = [0, 0, 0, 0, 0]
        v = randint(4700, 5500)
        i = randint(   0, 1000)
        data[1] = v % 256
        data[2] = v / 256
        data[3] = i % 256
        data[4] = i / 256
        return data

    class MockMsg2(object):
      mid = 0x19F30624
      @classmethod
      def get_data(cls):
        state = randint(2, 5)
        if state == 2:
          state = 0
        return [None, None, state]

    while True:
      time.sleep(1)
      listen_mppt(MockMsg1())
      time.sleep(1)
      listen_mppt(MockMsg2())

  thr = threading.Thread(target=mock_call_listen_mppt, args=(), kwargs={})
  thr.start()

else:
  usbtin = USBtin()
  usbtin.connect("/dev/ttyACM0")
  usbtin.add_message_listener(listen_mppt)
  usbtin.open_can_channel(250000, USBtin.ACTIVE)

bridge.loop()

if not MOCK:
  port.close()
