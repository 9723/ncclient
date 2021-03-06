from ncclient.operations.third_party.huawei.rpc import *
import unittest
from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from lxml import etree

cmd1 = '''
  <cmd>
    <id>1</id>
    <cmdline>display current-configuration</cmdline>
  </cmd>  
'''

action1 = '''
    <action>
      <aaa xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <cutUserByDomain>
          <domainName>huawei</domainName>
        </cutUserByDomain>
      </aaa>
    </action>
'''


class TestRPC(unittest.TestCase):

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.huawei.rpc.RPC._request')
    def test_cli(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'huawei'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = CLI(session, device_handler, raise_mode=RaiseMode.ALL)
        command = cmd1
        obj.request(command=command)
        node = new_ele("execute-cli", attrs={"xmlns":HW_PRIVATE_NS})
        node.append(validated_element(command))
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(etree.tostring(call), etree.tostring(node))

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.huawei.rpc.RPC._request')
    def test_action(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'huawei'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Action(session, device_handler, raise_mode=RaiseMode.ALL)
        action = action1
        obj.request(action=action)
        node = new_ele("execute-action", attrs={"xmlns":HW_PRIVATE_NS})
        node.append(validated_element(action))
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(etree.tostring(call), etree.tostring(node))

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.huawei.rpc.RPC._request')
    def test_get_next(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'huawei'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = GetNext(session, device_handler, raise_mode=RaiseMode.ALL)
        set_id = 39
        obj.request(set_id=set_id)
        node = new_ele("get-next",
                       attrs={"xmlns": HW_PRIVATE_NS, "set-id": str(set_id)})
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(etree.tostring(call), etree.tostring(node))

        device_handler1 = manager.make_device_handler({'name': 'huawei'})
        session1 = ncclient.transport.SSHSession(device_handler1)
        obj1 = GetNext(session1, device_handler1, raise_mode=RaiseMode.ALL)
        obj1.request(set_id=set_id, discard=True)
        node1 = new_ele("get-next",
                       attrs={"xmlns": HW_PRIVATE_NS, "set-id": str(set_id)})
        call1 = mock_request.call_args_list[0][0][0]
        self.assertEqual(call1.tag, node1.tag)
        self.assertEqual(etree.tostring(call1), etree.tostring(node1))
