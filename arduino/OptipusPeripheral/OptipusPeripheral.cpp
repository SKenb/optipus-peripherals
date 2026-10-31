#include "OptipusPeripheral.h"

OptipusPeripheral::OptipusPeripheral(Client& client, const char* host,
                                     uint16_t port, const char* peripheralId,
                                     const char* name)
    : client_(client), host_(host), port_(port),
      root_("peripheral"), name_(name) {}

String OptipusPeripheral::encode(const String& value) const {
  String result;
  for (size_t index = 0; index < value.length(); ++index) {
    const char character = value[index];
    if (isalnum(character) || character == '.' || character == '-' ||
        character == '_') {
      result += character;
    } else {
      char buffer[4];
      snprintf(buffer, sizeof(buffer), "%%%02X",
               static_cast<unsigned char>(character));
      result += buffer;
    }
  }
  return result;
}

bool OptipusPeripheral::setValue(const String& path, const String& value) {
  if (!client_.connect(host_.c_str(), port_)) {
    return false;
  }
  client_.print(String("GET /set/") + encode(path) + "/" + encode(value) +
                " HTTP/1.1\r\nHost: " + host_ +
                "\r\nConnection: close\r\n\r\n");
  while (client_.connected() && !client_.available()) {
    delay(1);
  }
  const bool received = client_.available();
  client_.stop();
  return received;
}

bool OptipusPeripheral::write(const char* node, const String& value) {
  return setValue(root_ + ".values." + node, value);
}

bool OptipusPeripheral::write(const char* node, float value) {
  return write(node, String(value, 3));
}

bool OptipusPeripheral::setErrorCode(uint16_t code) {
  if (code == 0) {
    return resetError();
  }
  errorCode_ = code;
  return setValue(root_ + ".status.errorFlag", String(errorCode_));
}

bool OptipusPeripheral::resetError() {
  errorCode_ = 0;
  return setValue(root_ + ".status.errorFlag", "0");
}

bool OptipusPeripheral::heartbeat(bool online, const char* error) {
  bool result = true;
  result &= setValue(root_ + ".meta.name", name_);
  result &= setValue(root_ + ".meta.platform", "arduino");
  result &= setValue(root_ + ".meta.protocolVersion", "1.0");
  result &= setValue(root_ + ".status.online", online ? "true" : "false");
  result &= setValue(root_ + ".status.lastError",
                     strlen(error) > 0 ? error : "No error");
  result &= setValue(root_ + ".status.errorFlag", String(errorCode_));
  return result;
}
