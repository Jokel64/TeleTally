#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Ticker.h>

#define RED D0
#define GREEN D1
#define BLUE D2

// 1, 2, 3 or 4
#define HOSTNAME_ID "1"
#define HOSTNAME "V-1HD Tally Light " HOSTNAME_ID

// 0, 1, 2 or 3
const int payload_index = 0;

const char* ssid = "RHEA";
const char* password = "igkultur";
const char* mqtt_server = "192.168.137.225";
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
long int value = 0;
uint8_t statusColor = BLUE;
Ticker ticker;
bool received_broadcast = false;
bool connected = false;

void turnAllLEDsOFF(){
  digitalWrite(GREEN, LOW);
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
}

void statusLEDChange(){
  digitalWrite(statusColor, !(digitalRead(statusColor)));
}

void startLEDChange(float sec, uint8_t color){
  ticker.detach();
  statusColor = color;
  turnAllLEDsOFF();
  ticker.attach(sec, statusLEDChange);
}

void stopLEDChange(){
  turnAllLEDsOFF();
  ticker.detach();
}

void noServer(){
  digitalWrite(GREEN, !(digitalRead(GREEN)));
  digitalWrite(RED, !(digitalRead(RED)));
}

void keepAlive(){
  client.publish("/feedback/alive", HOSTNAME_ID);
  if (received_broadcast){
    received_broadcast = false;
  } else {
    Serial.println("received_broadcast expired! No Backend connection!");
    ticker.detach();
    connected = false;
    turnAllLEDsOFF();
    ticker.attach(0.1, noServer);
  }
}

void startKeepAlive(){
  ticker.detach();
  Serial.println("Starting Keep Alive Packet");
  ticker.attach(5, keepAlive);
}

void init_wifi() {
  startLEDChange(0.1, BLUE);
  delay(500);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.hostname(HOSTNAME);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  stopLEDChange();
}

void callback(char* topic, byte* payload, unsigned int length) {
  turnAllLEDsOFF();
  received_broadcast = true;

  if (connected == false){
    Serial.println("(Re)-Connected to Backend.");
    connected = true;
    ticker.detach();
  }

  if (length != 4){
    Serial.println("Ill-Formed message!");
    return;
  }
  char state = payload[payload_index];
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
  startLEDChange(0.05, GREEN);
  Serial.print("Attempting MQTT connection...");
  String clientId = "Tally-";
  clientId += String(random(0xffff), HEX);
  while (!client.connected()) {
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.publish("/feedback/connected", HOSTNAME_ID);
      client.subscribe("/update");
      client.subscribe("/broadcast");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 1 seconds");
      delay(1000);
    }
  }
  stopLEDChange();
}

void setup() {
  pinMode(RED, OUTPUT);  
  pinMode(GREEN, OUTPUT);  
  pinMode(BLUE, OUTPUT);
  //pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  init_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED){
    init_wifi();
  }
  if (!client.connected()) {
    reconnect();
  }
  if (!ticker.active()){
    startKeepAlive();
  }
  client.loop();
}