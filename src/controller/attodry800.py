import time

from src.AttoDRY.PyAttoDRY import Cryostats, AttoDRY


def main():
    # Test the attodry800 controller
    print("Connect to the AttoDRY")
    attodry = AttoDRY(setup_version=Cryostats.ATTODRY800, com_port="COM5")

    try:
        attodry.begin()
        attodry.Connect()

        # you need to wait for initialization; if you just start sending
        # commands, the connection will be lost.
        time.sleep(10.0)

        initialized = attodry.isDeviceInitialised()
        connected = attodry.isDeviceConnected()

        # state that it is initialized and connected:
        if initialized and connected:
            print("The AttoDRY device is initialized and connected")
        else:
            print("something went wrong.")
            return

        pressure = attodry.getPressure800()
        user_temperature = attodry.getUserTemperature()
        turbo_pump_frequency = attodry.GetTurbopumpFrequ800()

        max_heat_power = attodry.getSampleHeaterMaximumPower()
        heat_power = attodry.getSampleHeaterPower()

        time.sleep(30)

        temperature = attodry.getSampleTemperature()
        lk_sample_temperature = attodry.get4KStageTemperature()

        print("The current pressure is: " + str(pressure) + " mbar")
        print("The current temperature is: " + str(temperature) + " K")
        print(
            "The current lk sample temperature is: " + str(lk_sample_temperature) + " K"
        )
        print("The current user temperature is: " + str(user_temperature) + " K")
        print(
            "The current turbo pump frequency is: " + str(turbo_pump_frequency) + " Hz"
        )

        print("The current maximum heat power is: " + str(max_heat_power) + " W")
        print("The current heat power is: " + str(heat_power) + " W")

        time.sleep(1.0)
    except Exception as e:
        print(e)
    finally:
        attodry.Disconnect()
        attodry.end()

    return


if __name__ == "__main__":
    main()
