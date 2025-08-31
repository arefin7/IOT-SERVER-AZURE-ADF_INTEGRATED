

#DPS SETTING

id_scope ="0ne00FF984B"
registration_id ="device3"
cert_file="/home/pi/iot-server/certs/certs/device3.pem"
key_file ="/home/pi/iot-server/certs/certs/device3.key"

import asyncio
import json
import random
from azure.iot.device.aio import ProvisioningDeviceClient, IoTHubDeviceClient
from azure.iot.device import X509



async def main():
    # X.509 setup
    x509 = X509(cert_file, key_file, None)

    # Provisioning step
    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host="global.azure-devices-provisioning.net",
        registration_id=registration_id,
        id_scope=id_scope,
        x509=x509
    )

    result = await provisioning_device_client.register()
    print("? DPS result:", result)

    if result.status == "assigned":
        print(f"? Device {registration_id} assigned to IoT Hub {result.registration_state.assigned_hub}")

        # Create IoT Hub client
        device_client = IoTHubDeviceClient.create_from_x509_certificate(
            x509=x509,
            hostname=result.registration_state.assigned_hub,
            device_id=result.registration_state.device_id,
        )

        await device_client.connect()

        # Send sample telemetry forever
        while True:
            data = {
                "temperature": round(random.uniform(20, 30), 2),
                "rpm": random.randint(700, 900),
                "status": "running"
            }
            print("?? Sending message:", data)
            await device_client.send_message(json.dumps(data))
            await asyncio.sleep(5)  # send every 5 sec

asyncio.run(main())




