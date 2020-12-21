#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define RED D0
#define GREEN D1
#define BLUE D2

// Update these with values suitable for your network.

const char* ssid = "RHEA";
const char* password = "igkultur";
const char* mqtt_server = "192.168.137.225";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
long int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.hostname("EMT V-1HD Tally Light 1");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(BLUE, HIGH);
    delay(100);
    digitalWrite(BLUE, LOW);
    delay(100);
    Serial.print(".");
    delay(500);
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  digitalWrite(GREEN, LOW);
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
  if (length != 4){
    Serial.println("Ill-Formed message!");
    return;
  }
  char state = payload[0];
  if(state == 'r'){
        digitalWrite(GREEN, HIGH);
      } else if(state == 'l'){
        digitalWrite(RED, HIGH);
      } else if (state == 'n'){
        digitalWrite(BLUE, HIGH);
      } else {
        digitalWrite(GREEN, HIGH);
        digitalWrite(RED, HIGH);
        digitalWrite(BLUE, HIGH);
      }

  Serial.println(state);

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    digitalWrite(GREEN, HIGH);
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("/update");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 1 seconds");
      // Wait 5 seconds before retrying
      digitalWrite(GREEN, LOW);

      delay(1000);
    }
  }
}

void setup() {
  pinMode(RED, OUTPUT);  
  pinMode(GREEN, OUTPUT);  
  pinMode(BLUE, OUTPUT);
  //pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

}
/*
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
 
  delay(300);
}
*/