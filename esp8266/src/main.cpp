#include <Arduino.h>
#include <esp8266wifi.h>
#include <esp8266httpclient.h>

#define RED D0
#define GREEN D1
#define BLUE D2
#define SSID "RHEA"
#define PASSSWORD "igkultur"

void setup() {
  pinMode(RED, OUTPUT);  
  pinMode(GREEN, OUTPUT);  
  pinMode(BLUE, OUTPUT);

  Serial.begin(115200);
  WiFi.hostname("EMT V-1HD Tally Light 1");
  WiFi.begin(SSID, PASSSWORD);
  
  Serial.print("Connecting..");
  while (WiFi.status() != WL_CONNECTED) {
 
    digitalWrite(BLUE, HIGH);
    delay(100);
    digitalWrite(BLUE, LOW);
    delay(100);
    Serial.print(".");
    delay(500);
  }
  digitalWrite(D2, LOW);
  Serial.println("");
  Serial.println("Connected.");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) { //Check WiFi connection status
 
    HTTPClient http;  //Declare an object of class HTTPClient

    http.begin("http://"+ WiFi.gatewayIP().toString() + ":5000/api/v1/tally/s/1");  //Specify request destination
    int httpCode = http.GET();                                  //Send the request
    digitalWrite(GREEN, LOW);
    digitalWrite(RED, LOW);
    digitalWrite(BLUE, LOW);
    
    if(httpCode > 0) { //Check the returning code
      String payload = http.getString();   //Get the request response payload
      Serial.println(payload);             //Print the response payload
      if(payload.equals("ready")){
        digitalWrite(GREEN, HIGH);
      } else if(payload.equals("live")){
        digitalWrite(RED, HIGH);
      } else {
        digitalWrite(BLUE, HIGH);
      }
    }
 
    http.end();   //Close connection
 
  } else {
    digitalWrite(GREEN, LOW);
    digitalWrite(RED, LOW);
    digitalWrite(BLUE, HIGH);
    delay(100);
    digitalWrite(BLUE, LOW);
    delay(100);
  }
 
  delay(200);
}