###### \# 1. CREATE RESOURCE GROUP

## 

az group create -l centralindia -n mygroup



###### \# 2. IoT hub Create

az iot hub create --name textile-iothub --resource-group mygroup --sku S1 --location centralindia --partition-count 2 --retention-day 7





###### \# 3. data push Rpi--> AZURE IOT HUB



Option A: Use Python + Azure SDK (azure-iot-device)

Best for secure and scalable deployments



Supports device twin, cloud-to-device messaging, etc.





###### \- Create a device identity



az iot hub device-identity create --device-id pi-gateway --hub-name textile-iothub



###### -Get its connection string



az iot hub device-identity connection-string show --device-id pi-gateway --hub-name textile-iothub --output tsv





4\. Push Data Using Python SDK



pip install azure-iot-device





//////



from azure.iot.device import IoTHubDeviceClient, Message

import random

import time



CONNECTION\_STRING = "HostName=textile-iothub.azure-devices.net;DeviceId=pi-gateway;SharedAccessKey=wF1h2B+VzM2xGqC1X5DZfFt6tH2pGR1ZddQ6V2pMF7s="



def main():

    client = IoTHubDeviceClient.create\_from\_connection\_string(CONNECTION\_STRING)



    while True:

        rpm = random.randint(500, 1200)

        temperature = random.uniform(28.0, 60.0)

        message = Message(f'{{"rpm": {rpm}, "temperature": {temperature:.2f}}}')

        print("Sending message:", message)

        client.send\_message(message)

        time.sleep(5)



if \_\_name\_\_ == "\_\_main\_\_":

    main()



///





5.CRETE DPS :



az iot dps create \\

  --name textile-dps \\

  --resource-group iot-rg \\

  --location centralindia \\

  --sku S1





6\. Link DPS to Your IoT Hub



az iot dps linked-hub create \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --connection-string "$(az iot hub show-connection-string --name textile-iothub --resource-group iot-rg --output tsv)" \\

  --location centralindia







7\. Device Enrollment (Symmetric Key-based)



az iot dps enrollment create \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --enrollment-id esp32-device-001 \\

  --attestation-type symmetricKey \\

  --device-id esp32-device-001





🔑 You’ll get:



Primary Key



Secondary Key



ID Scope of the DPS instance





\*\*8. Get the DPS ID Scope:



az iot dps show \\

  --name textile-dps \\

  --resource-group iot-rg \\

  --query properties.idScope \\

  --output tsv





Example:



o/p: 0ne000A1B2C





9\. If edge device is raspi: Code-->

pip install azure-iot-device



......................provision\_and\_send.py.....................









from azure.iot.device import ProvisioningDeviceClient, IoTHubDeviceClient, Message



id\_scope = "your-dps-id-scope"

registration\_id = "esp32-device-001"

symmetric\_key = "base64-symmetric-key"



provisioning\_host = "global.azure-devices-provisioning.net"



provisioning\_client = ProvisioningDeviceClient.create\_from\_symmetric\_key(

    provisioning\_host=provisioning\_host,

    registration\_id=registration\_id,

    id\_scope=id\_scope,

    symmetric\_key=symmetric\_key

)



registration\_result = provisioning\_client.register()



print("Provisioning result:", registration\_result.status)



if registration\_result.status == "assigned":

    device\_client = IoTHubDeviceClient.create\_from\_symmetric\_key(

        symmetric\_key=symmetric\_key,

        hostname=registration\_result.registration\_state.assigned\_hub,

        device\_id=registration\_id

    )



    device\_client.connect()

    msg = Message('{"temperature": 45, "rpm": 890}')

    device\_client.send\_message(msg)

    print("Message sent!")

else:

    print("Provisioning failed")















If edge device is ESP32..............

.........................................ESP32 CODE...................





\#include <WiFi.h>

\#include <AzureIoTHub.h>

\#include <AzureIoTProtocol\_MQTT.h>

\#include <AzureIoTProvisioning.h>

\#include <AzureIoTUtility.h>



// WiFi Credentials

const char\* ssid     = "YourSSID";

const char\* password = "YourPassword";



// DPS Info

const char\* idScope = "0ne000XXXXX";             // Your DPS ID Scope

const char\* registrationId = "esp32-01";         // Must match DPS

const char\* symmetricKey = "your\_primary\_key=="; // From DPS Enrollment group



IOTHUB\_DEVICE\_CLIENT\_LL\_HANDLE device\_ll\_handle;



void setup() {

  Serial.begin(115200);

  WiFi.begin(ssid, password);



  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL\_CONNECTED) {

    delay(500);

    Serial.print(".");

  }

  Serial.println("Connected");



  // Register device with DPS

  PROV\_DEVICE\_LL\_HANDLE prov\_handle;

  prov\_handle = Prov\_Device\_LL\_CreateFromSymmetricKey(

    MQTT\_Protocol, idScope, registrationId, symmetricKey

  );



  if (prov\_handle == NULL) {

    Serial.println("Provisioning failed!");

    return;

  }



  Serial.println("Provisioned. Getting IoT Hub handle...");



  device\_ll\_handle = Prov\_Device\_LL\_Register\_Device(prov\_handle);



  if (device\_ll\_handle == NULL) {

    Serial.println("Failed to get device handle");

    return;

  }



  Serial.println("Device registered with IoT Hub.");

}



void loop() {

  IOTHUB\_MESSAGE\_HANDLE message\_handle;

  const char\* telemetry = "{\\"temperature\\": 28.5, \\"rpm\\": 850}";



  message\_handle = IoTHubMessage\_CreateFromString(telemetry);

  IoTHubDeviceClient\_LL\_SendEventAsync(device\_ll\_handle, message\_handle, NULL, NULL);

  IoTHubMessage\_Destroy(message\_handle);



  IoTHubDeviceClient\_LL\_DoWork(device\_ll\_handle); // Required for SDK background tasks

  delay(10000); // Send every 10s

}







...............................................................................



🔐 What is X.509 in Azure IoT?





X.509 certificates are a secure method of authenticating devices to Azure IoT Hub/DPS. Instead of symmetric keys, each device (like ESP32 or Raspberry Pi) has:



A private key (stored securely on device)



A public certificate



A root CA or intermediate CA that Azure trusts



🔄 Where X.509 Fits in Your Setup

Component	Role of X.509 Cert

ESP32 Clients	Each ESP32 gets a device certificate + private key and uses it to authenticate with DPS

Azure DPS	Verifies ESP32's certificate using a trusted root CA

IoT Hub	Receives verified device registration from DPS and allows secure connection



.....................................................................................







Step-1:

mkdir azure-iot-cert \&\& cd azure-iot-cert







step-2: *Generate Root CA*





openssl genrsa -out rootCA.key 2048





openssl req -x509 -new -nodes \\

    -key rootCA.key \\

    -sha256 -days 1024 \\

    -out rootCA.pem \\

    -subj "/CN=TextileIoT-RootCA"









Output : it will generate two file:
rootCA.key (Private key)



rootCA.pem (Public certificate)





Step 3: *Create Intermediate CA certificate signed by the Root CA.*



openssl genrsa -out intermediateCA.key 2048







openssl req -new -key intermediateCA.key \\

  -out intermediateCA.csr \\

  -subj "/CN=TextileIoT-IntermediateCA"







step-4:  Sign the CSR with Root CA to issue Intermediate CA certificate:



 openssl x509 -req -in intermediateCA.csr \\

  -CA rootCA.pem -CAkey rootCA.key -CAcreateserial \\

  -out intermediateCA.pem -days 500 -sha256







\*\*\*\* After these commands, you should have:



intermediateCA.key

intermediateCA.csr

intermediateCA.pem

rootCA.pem

rootCA.key

rootCA.srl    ← (Serial number file auto-created)



..........................................................



Step 5: Create the device certificate signed by the Intermediate CA.





Generate private key for the device



openssl genrsa -out device.key 2048







-->Create Certificate Signing Request (CSR) for the device







openssl req -new -key device.key \\

  -out device.csr \\

  -subj "/CN=esp32-device"



Note : Replace "esp32-device" with your device ID





step-5: Sign the device CSR using the Intermediate CA





openssl x509 -req -in device.csr \\

  -CA intermediateCA.pem -CAkey intermediateCA.key -CAcreateserial \\

  -out device.pem -days 365 -sha256









After this step, you will have:



device.key         ← Device’s private key

device.csr         ← CSR for the device

device.pem         ← Device certificate signed by Intermediate CA

intermediateCA.pem ← Intermediate CA certificate







step-6:  Register Root CA in Azure DPS and Verify



You must use Root CA, not intermediate, for verification in Azure DPS.





az iot dps certificate create \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --certificate-name textile-rootCA \\

  --path rootCA.pem





Get the verification code:





output:  "verificationCode": "CN=verification-cert-textile-rootCA-xyz..."





step-7: Create a verification certificate







openssl req -new -key rootCA.key \\

  -out verification.csr \\

  -subj "/CN=verification-cert-textile-rootCA-xyz..."



openssl x509 -req -in verification.csr \\

  -CA rootCA.pem -CAkey rootCA.key -CAcreateserial \\

  -out verification.pem -days 365 -sha256





\*\*\*\*\*\*\*Complete verification in DPS





az iot dps certificate verify \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --certificate-name textile-rootCA \\

  --path verification.pem



✅ Success: Your CA is now verified.







Step 8: Create Enrollment Group in Azure DPS using the Verified CA



This step tells Azure DPS to trust devices signed by your Intermediate CA (chained from the Root CA). All ESP32 clients with such certs can auto-register securely.











Create Enrollment Group (X.509 CA-based)



az iot dps enrollment-group create \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --enrollment-id textile-enroll-group \\

  --certificate-name textile-rootCA \\

  --provisioning-status enabled \\

  --iot-hub-host-name textile-iothub.azure-devices.net \\

  --attestation-type x509





✅ This links your Root CA certificate to an enrollment group so any device with a signed certificate chain will be allowed.





step-9: Confirm Enrollment Group Creation



az iot dps enrollment-group show \\

  --dps-name textile-dps \\

  --resource-group iot-rg \\

  --enrollment-id textile-enroll-group









✅ Outcome

You now have:



🏷️ An enrollment group called textile-enroll-group



🛡️ That uses textile-rootCA for secure authentication



🔗 Linked to your IoT Hub (textile-iothub)









\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*Raspberry Pi Client (Python Azure IoT SDK)....

📁 Folder structure:



raspi\_x509/

├── certs/

│   ├── device\_cert.pem        # Device certificate (CN must match registration\_id)

│   ├── device\_key.pem         # Private key for the device

│   └── root\_ca.pem            # Root CA (used for verification of Azure's server cert)

├── x509\_dps\_client.py         # Main Python script





............................x509\_dps\_client.py:...........................





from azure.iot.device import X509, ProvisioningDeviceClient, IoTHubDeviceClient

import os



\# ---------------------------

\# STEP 1: Replace with yours

\# ---------------------------

id\_scope = "<your-id-scope>"

registration\_id = "raspi-device-001"  # CN in cert should match this

provisioning\_host = "global.azure-devices-provisioning.net"



cert\_path = "certs/device\_cert.pem"

key\_path = "certs/device\_key.pem"

root\_ca\_path = "certs/root\_ca.pem"  # Optional unless validating Azure's cert

passphrase = None  # Set if private key is encrypted



\# ---------------------------

\# STEP 2: Create X.509 object

\# ---------------------------

x509 = X509(

    cert\_file=cert\_path,

    key\_file=key\_path,

    pass\_phrase=passphrase

)



\# ---------------------------

\# STEP 3: Connect to DPS

\# ---------------------------

print("Connecting to Azure DPS using X.509...")

provisioning\_client = ProvisioningDeviceClient.create\_from\_x509\_certificate(

    provisioning\_host=provisioning\_host,

    registration\_id=registration\_id,

    id\_scope=id\_scope,

    x509=x509

)



registration\_result = provisioning\_client.register()

print("Provisioning result:", registration\_result.status)



if registration\_result.status != "assigned":

    print("Device not assigned. Exiting.")

    exit(1)



\# ---------------------------

\# STEP 4: Connect to IoT Hub

\# ---------------------------

print("Assigned Hub:", registration\_result.registration\_state.assigned\_hub)

print("Device ID:", registration\_result.registration\_state.device\_id)



device\_client = IoTHubDeviceClient.create\_from\_x509\_certificate(

    x509=x509,

    hostname=registration\_result.registration\_state.assigned\_hub,

    device\_id=registration\_result.registration\_state.device\_id

)



print("Connecting to IoT Hub...")

device\_client.connect()



\# ---------------------------

\# STEP 5: Send test message

\# ---------------------------

device\_client.send\_message("Hello from Raspberry Pi via DPS + X.509!")

print("Message sent successfully.")



device\_client.disconnect()

print("Disconnected.")













