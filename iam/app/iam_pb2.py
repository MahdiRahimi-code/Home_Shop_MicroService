# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: iam.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'iam.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tiam.proto\x12\x03iam\"!\n\x0eGetUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\"o\n\x0fGetUserResponse\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05\x65mail\x18\x03 \x01(\t\x12\x0c\n\x04\x63ity\x18\x04 \x01(\t\x12\x11\n\tis_active\x18\x05 \x01(\x08\x12\x12\n\navatar_url\x18\x06 \x01(\t\"\x87\x01\n\x11UpdateUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\x12\x32\n\x06\x66ields\x18\x02 \x03(\x0b\x32\".iam.UpdateUserRequest.FieldsEntry\x1a-\n\x0b\x46ieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\" \n\x12UpdateUserResponse\x12\n\n\x02ok\x18\x01 \x01(\x08\"%\n\x11\x41\x64minCheckRequest\x12\x10\n\x08\x61\x64min_id\x18\x01 \x01(\x05\"A\n\x12\x41\x64minCheckResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x10\n\x08is_admin\x18\x03 \x01(\x08\"$\n\x11\x44\x65leteUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\"%\n\x12\x44\x65leteUserResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"!\n\x0e\x42\x61nUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\"\"\n\x0f\x42\x61nUserResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xb5\x02\n\nIAMService\x12\x34\n\x07GetUser\x12\x13.iam.GetUserRequest\x1a\x14.iam.GetUserResponse\x12=\n\nUpdateUser\x12\x16.iam.UpdateUserRequest\x1a\x17.iam.UpdateUserResponse\x12=\n\nCheckAdmin\x12\x16.iam.AdminCheckRequest\x1a\x17.iam.AdminCheckResponse\x12=\n\nDeleteUser\x12\x16.iam.DeleteUserRequest\x1a\x17.iam.DeleteUserResponse\x12\x34\n\x07\x42\x61nUser\x12\x13.iam.BanUserRequest\x1a\x14.iam.BanUserResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'iam_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_UPDATEUSERREQUEST_FIELDSENTRY']._loaded_options = None
  _globals['_UPDATEUSERREQUEST_FIELDSENTRY']._serialized_options = b'8\001'
  _globals['_GETUSERREQUEST']._serialized_start=18
  _globals['_GETUSERREQUEST']._serialized_end=51
  _globals['_GETUSERRESPONSE']._serialized_start=53
  _globals['_GETUSERRESPONSE']._serialized_end=164
  _globals['_UPDATEUSERREQUEST']._serialized_start=167
  _globals['_UPDATEUSERREQUEST']._serialized_end=302
  _globals['_UPDATEUSERREQUEST_FIELDSENTRY']._serialized_start=257
  _globals['_UPDATEUSERREQUEST_FIELDSENTRY']._serialized_end=302
  _globals['_UPDATEUSERRESPONSE']._serialized_start=304
  _globals['_UPDATEUSERRESPONSE']._serialized_end=336
  _globals['_ADMINCHECKREQUEST']._serialized_start=338
  _globals['_ADMINCHECKREQUEST']._serialized_end=375
  _globals['_ADMINCHECKRESPONSE']._serialized_start=377
  _globals['_ADMINCHECKRESPONSE']._serialized_end=442
  _globals['_DELETEUSERREQUEST']._serialized_start=444
  _globals['_DELETEUSERREQUEST']._serialized_end=480
  _globals['_DELETEUSERRESPONSE']._serialized_start=482
  _globals['_DELETEUSERRESPONSE']._serialized_end=519
  _globals['_BANUSERREQUEST']._serialized_start=521
  _globals['_BANUSERREQUEST']._serialized_end=554
  _globals['_BANUSERRESPONSE']._serialized_start=556
  _globals['_BANUSERRESPONSE']._serialized_end=590
  _globals['_IAMSERVICE']._serialized_start=593
  _globals['_IAMSERVICE']._serialized_end=902
# @@protoc_insertion_point(module_scope)
