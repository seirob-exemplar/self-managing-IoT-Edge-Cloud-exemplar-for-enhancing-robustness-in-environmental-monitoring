import grpc
import setup
from chirpstack_api import api

# This must point to the API interface.
server = setup.ip
api_token = setup.api_token

def get_device_list(application_id, limit, offset):

    channel = grpc.insecure_channel(server)
    client = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListDevicesRequest()
    req.application_id = application_id
    req.limit = limit
    req.offset = offset
    
    resp = client.List(req, metadata=auth_token)
    return resp


def get_gateway_list(limit, offset):

    channel = grpc.insecure_channel(server)
    client = api.GatewayServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListGatewaysRequest()
    req.limit = limit
    req.offset = offset

    resp = client.List(req, metadata=auth_token)
    return resp


def get_device_key(dev_eui):

    channel = grpc.insecure_channel(server)
    client = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.DeviceKeys()
    req.dev_eui = dev_eui

    resp = client.GetKeys(req, metadata=auth_token)
    return resp


# def get_last_gateway_ping(gateway_id):

#     channel = grpc.insecure_channel(server)
#     client = api.GatewayServiceStub(channel)
#     auth_token = [("authorization", "Bearer %s" % api_token)]

#     gateway_id_hex = int(gateway_id, 16).to_bytes(8, 'big').hex()
#     # Construct request.
#     req = api.GatewayService.
#     req.gateway_id = gateway_id_hex

#     resp = client.GetLastPing(req, metadata=auth_token)
#     return resp


def enqueue_device_downlink(dev_eui, f_port, confirmed, data):
    
    channel = grpc.insecure_channel(server)
    client =  api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.EnqueueDeviceQueueItemRequest()
    req.queue_item.confirmed = confirmed
    req.queue_item.data = bytes(data.encode())
    req.queue_item.dev_eui = dev_eui
    req.queue_item.f_port = f_port

    resp = client.Enqueue(req, metadata=auth_token)
    #print(resp.id)

#Example enqueue
#   channel = grpc.insecure_channel(server)

#     Device-queue API client.
#     client = api.DeviceServiceStub(channel)

#     Define the API key meta-data.
#     auth_token = [("authorization", "Bearer %s" % api_token)]

#     comando = "timetosend|20000|timetoreceive|10000|" #comando da inviare all'arduino
#     codificaCmd = comando.encode("utf-8") # codifico il comando (in byte)
#     codificaCmd = codificaCmd.decode("utf-8") 

#     Construct request.
#     req = api.EnqueueDeviceQueueItemRequest()
#     req.queue_item.confirmed = False
#     req.queue_item.data = codificaCmd
#     req.queue_item.dev_eui = dev_eui
#     req.queue_item.f_port = 1

#     resp = client.Enqueue(req, metadata=auth_token)

#     Print the downlink id
#     print(resp.id)