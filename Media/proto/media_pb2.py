# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: media.proto
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
    'media.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bmedia.proto\x12\x05media\x1a\x1bgoogle/protobuf/empty.proto\"N\n\x1bUploadProfilePictureRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"O\n\x19UploadProductImageRequest\x12\x12\n\nproduct_id\x18\x01 \x01(\t\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\")\n\x14RemovePictureRequest\x12\x11\n\timage_url\x18\x01 \x01(\t\"-\n\rMediaResponse\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\">\n\x19ProfilePictureMetaRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\".\n\x1bRemoveProfilePictureRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\"-\n\x19RemoveProductImageRequest\x12\x10\n\x08media_id\x18\x01 \x01(\t\"4\n\x13UploadMediaResponse\x12\x10\n\x08media_id\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t2\xb6\x03\n\x0cMediaService\x12V\n\x14UploadProfilePicture\x12\".media.UploadProfilePictureRequest\x1a\x1a.media.UploadMediaResponse\x12R\n\x14RemoveProfilePicture\x12\".media.RemoveProfilePictureRequest\x1a\x16.google.protobuf.Empty\x12R\n\x12UploadProductImage\x12 .media.UploadProductImageRequest\x1a\x1a.media.UploadMediaResponse\x12N\n\x12RemoveProductImage\x12 .media.RemoveProductImageRequest\x1a\x16.google.protobuf.Empty\x12V\n\x16SaveProfilePictureMeta\x12 .media.ProfilePictureMetaRequest\x1a\x1a.media.UploadMediaResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'media_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_UPLOADPROFILEPICTUREREQUEST']._serialized_start=51
  _globals['_UPLOADPROFILEPICTUREREQUEST']._serialized_end=129
  _globals['_UPLOADPRODUCTIMAGEREQUEST']._serialized_start=131
  _globals['_UPLOADPRODUCTIMAGEREQUEST']._serialized_end=210
  _globals['_REMOVEPICTUREREQUEST']._serialized_start=212
  _globals['_REMOVEPICTUREREQUEST']._serialized_end=253
  _globals['_MEDIARESPONSE']._serialized_start=255
  _globals['_MEDIARESPONSE']._serialized_end=300
  _globals['_PROFILEPICTUREMETAREQUEST']._serialized_start=302
  _globals['_PROFILEPICTUREMETAREQUEST']._serialized_end=364
  _globals['_REMOVEPROFILEPICTUREREQUEST']._serialized_start=366
  _globals['_REMOVEPROFILEPICTUREREQUEST']._serialized_end=412
  _globals['_REMOVEPRODUCTIMAGEREQUEST']._serialized_start=414
  _globals['_REMOVEPRODUCTIMAGEREQUEST']._serialized_end=459
  _globals['_UPLOADMEDIARESPONSE']._serialized_start=461
  _globals['_UPLOADMEDIARESPONSE']._serialized_end=513
  _globals['_MEDIASERVICE']._serialized_start=516
  _globals['_MEDIASERVICE']._serialized_end=954
# @@protoc_insertion_point(module_scope)
