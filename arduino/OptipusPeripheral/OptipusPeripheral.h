#pragma once

#include <Arduino.h>
#include <Client.h>

class OptipusPeripheral {
public:
  OptipusPeripheral(Client& client, const char* host, uint16_t port,
                    const char* peripheralId, const char* name);
  bool write(const char* node, const String& value);
  bool write(const char* node, float value);
  bool setErrorCode(uint16_t code);
  bool resetError();
  bool heartbeat(bool online = true, const char* error = "");

private:
  bool setValue(const String& path, const String& value);
  String encode(const String& value) const;
  Client& client_;
  String host_;
  uint16_t port_;
  String root_;
  String name_;
  uint16_t errorCode_ = 0;
};
