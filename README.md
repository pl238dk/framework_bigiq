# BIG-IQ Framework

This is a framework that connects to the API of a BIG-IQ device.

## Authentication

Credentials are stored in JSON format, in the same directory as the `bigiq.py` file. The name of the file should be `credentials.json`.

Other authentication methods, such as KDBX, have been tested, but this way it keeps the hard-coded passwords out of the source code.

```
{
    "arbitrary_name": {
        "host": "",
        "username": "",
        "password": ""
    }
}
```

The name of the credentials is arbitrary and references parameters for hostname/ip, username, and password.

API calls will be made to `https://` + host.

A separate function `login()` will need to be called in order to authenticate to the BIG-IQ device.

## Getting Started

To instantiate a `BigIQ` object, pass a string of the credential name created in the "Authentication" section :

```
>>> credential_name = 'arbitrary_name'
>>> b = BigIQ(credential_name)
```

Then to log in, execute the `login()` function.

```
>>> b.login()
```

## BIG-IQ Features

Three main subsections define the API structure:
- TM (traffic management)
- CM (centralized management)
- shared (shared infrastructure)

Most interactions to the BIG-IQ appliance regarding tenants are going to be performed with the CM subsection.

To find a list of devices, query the ADC section of the `shared` utility :

```
>>> b.get_adc_device()
```