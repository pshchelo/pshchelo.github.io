################################################################
Authentication flow with Keystone and OpenID Connect - with cURL
################################################################

.. |date| date::

:date: 2024-06-12
:modified: |date|
:tags: openstack,keystone,federation,openid,oidc,curl
:category: work
:slug: keystone-oidc-curl
:lang: en
:authors: pas-ha
:summary: auth to keystone federated via oidc with cURL calls


Recently I was tasked to provide an example curl commands to realize the
authentication process required to get an OpenStack Identity (Keystone) token
for a user federated via OpenID Connect.
Usually we tend to use already established libraries like
``keystoneauth`` or ``gophercloud`` for that, but since I not so long ago
had to dive into OpenID Connect anyway, this posed  an interesting task.

I use
`Mirantis OpenStack for Kubernetes <https://www.mirantis.com/software/mirantis-openstack-for-kubernetes/>`_
(naturally :-) ), that integrates
Keystone with Keycloak via OpenID Connect, OpenStack release is Caracal.


Pre-requisites
==============

- OpenStack deployed and configured to use federation via OpenID Connect.
- Account in the Identity Provider allowing you to login to OpenStack.
- ``curl`` and ``jq`` installed and available.

Required access info
--------------------
Obtain required access info.
The commands below expect the following environment variables to be available.

OS_AUTH_URL
  the OpenStack Identity endpoint address. Note that examples below expect
  a versioned endpoint (ends with ``/v3``), adapt URLs accordingly if yours
  is not versioned.

OS_DISCOVERY_ENDPOINT
  the URL of OpenID configuration discovery of the Identity Provider configured
  in Keystone, usually ends with ``.../.well-known/openid-configuration``.

OS_IDENTITY_PROVIDER
  Name of the identity provider configured in Keystone.

OS_PROTOCOL
  Name of the protocol configured for this Identity Provider in Keystone.

OS_CLIENT_ID
  The client name to use when contacting Identity Provider.
  Note - this is NOT your OpenStack login.

OS_CLIENT_SECRET
  The password to use for the Identity Provider client.
  Usually it must be kept secret,
  as in standard Web SSO application of OpenID Connect,
  but here, as with Kubernetes + OpenID Connect,
  the CLI client is required to know it.
  Some Identity Providers allow to create clients without secrets (for example
  Keycloak does allow that).

OS_OPENID_SCOPE
  The scope to use for authentication, governs how much info about you the
  Identity Provider will pass to the Service Provider - in this case you :-)
  At least (and usually only) must be ``openid``.

OS_USERNAME
  Your username with Identity Provider you want to login to OpenStack with.

OS_PASSWORD
  Your password for your account with the Identity Provider.

OS_PROJECT_NAME
  The name of the OpenStack project you want to authenticate to.

OS_PROJECT_DOMAIN_ID
  ID of the OpenStack Identity domain that project belongs to.

Get it from Horizon
~~~~~~~~~~~~~~~~~~~
The easiest way to obtain those is to login via federation to Horizon,
and download the RC file from the UI:

.. image:: {static}/images/keystone-oidc-curl/horizon-download-rc-file.png

source this file into the active shell, it will ask you for your password

.. code-block:: bash

   source <project>-openrc.sh

In what follows, I am assuming you've done that already, so all the necessary
environment variables are present.

Authentication Flow
===================

Now let's start with curl-ing. I use ``-sk`` to silence the progress indicator
and, since I use development toy environment and self-signed TLS certificates,
ignore TLS verification failures.

I am following the calls that would've been made when using ``keystoneauth``
library with ``v3oidcpassword`` authentication type.


Get OIDC token endpoint
-----------------------

Using the discovery endpoint, find the URL of token endpoint:

.. code-block:: bash

   token_endpoint=$(curl -sk -X GET $OS_DISCOVERY_ENDPOINT | jq -r .token_endpoint)


Get the OIDC access token
-------------------------

.. code-block:: bash

   access_token=$(curl -sk \
       -X POST $token_endpoint \
       -u $OS_CLIENT_ID:$OS_CLIENT_SECRET \
       -d "username=${OS_USERNAME}&password=${OS_PASSWORD}&scope=${OS_OPENID_SCOPE}&grant_type=password" \
       -H "Content-Type: application/x-www-form-urlencoded" \
       | jq -r .access_token)

The trick is the Content-Type - as per the
`OpenID Connect RFC <https://openid.net/specs/openid-connect-core-1_0.html#TokenRequest>`_
this is how it must be done with Form Serialization, not JSON.
The client id and client secret are used for HTTP Basic Authentication, again,
as per that RFC.

Get the unscoped Keystone token
-------------------------------

Now the OpenStack part. In OpenStack, tokens are issued and valid in various
"scopes" - project, domain, system or unscoped.

With federation, API user is expected to first exchange the Identity Provider
token for unscoped OpenStack Identity token:

.. code-block:: bash

   unscoped_token=$(curl -sik \
       -I \
       -X POST $OS_AUTH_URL/OS-FEDERATION/identity_providers/${OS_IDENTITY_PROVIDER}/protocols/${OS_PROTOCOL}/auth \
       -H "Authorization: Bearer $access_token" \
       | grep x-subject-token \
       | awk '{print $2}' \
       | tr -d '\r')

(the result of grep + awk has new line in the end, so need to trim that out
to put that value properly into JSON later).

Here already we have some inconveniences with Bash:
the token arrives in the header, but the response body (in JSON)
also has some info.
We are ignoring it, but it may be quite useful in some applications.

Discover authentication scopes (optional)
-----------------------------------------

If you do not have the intended scope of authentication at hand - project or
domain or system - you can now discover the available to you scopes by making
the following requests with unscoped token:

.. code-block:: bash

   curl -sik $OS_AUTH_URL/auth/projects -H "X-Auth-Token: $unscoped_token" | jq .projects
   curl -sik $OS_AUTH_URL/auth/domains -H "X-Auth-Token: $unscoped_token" | jq .domains
   curl -sik $OS_AUTH_URL/auth/system -H "X-Auth-Token: $unscoped_token" | jq .system

Prepare JSON for scoped token request
-------------------------------------

Generating JSON in Bash is very awkward due to double-quotes and lots of
escaping... just save the request JSON body to file (obviously not secure):


.. code-block:: bash

   token_request=$(mktemp)
   cat > $token_request << EOJSON
   {
     "auth": {
       "identity": {
         "methods": [
           "token"
         ],
         "token": {
           "id": "$unscoped_token"
         }
       },
       "scope": {
         "project": {
           "domain": {
             "id": "$OS_PROJECT_DOMAIN_ID"
           },
           "name": "$OS_PROJECT_NAME"
         }
       }
     }
   }
   EOJSON

Get scoped token
----------------

Biggest disadvantages here, as again, the token is in the headers,
but the response body contains a lot of useful info, including auth info
(UUIDs of project, domain etc, group assignments, roles if explicit),
and the Identity Catalog to discover the actual URL of the service endpoints
we want to acces with the received token.
Again, we skip all that useful info and only fetch the token:

.. code-block:: bash

   scoped_token=$(curl -sik \
       -X POST $OS_AUTH_URL/auth/tokens \
       -d "@$token_request" -H "Content-Type: application/json" \
       | grep x-subject-token \
       | awk '{print $2}' \
       | tr -d '\r')


Remove the temporary file with token request body (tiny security improvement):

.. code-block:: bash

   rm $token_request

Use scoped token to make request to an OpenStack service
========================================================
Here hardcoded endpoint is used, however base part of it could've
been discovered from the response body of the previous request.

Get the list of available images:

.. code-block:: bash

   curl -sk \
       -X GET https://glance.it.just.works/v2/images \
       -H "X-Auth-Token: $scoped_token" \
       | jq .images

I specifically use Glance in the example as it has no project UUID in the
endpoint, but many more services will need that, so their endpoints are better
to discover from the catalog that was in the body of the response when we got
ourselves the scoped token in the previous step.

The same but in Python
======================

For comparison here are examples using Python:

requests only
-------------
first, very manual example using ``requests`` only, but now with proper
discovery of service endpoint:

.. code-block:: python

    #!/usr/bin/env python
    import os
    import requests

    fed_auth = {
        "os_discovery_endpoint": os.getenv("OS_DISCOVERY_ENDPOINT"),
        "os_identity_provider": os.getenv("OS_IDENTITY_PROVIDER"),
        "os_protocol": os.getenv("OS_PROTOCOL"),
        "os_openid_scope": os.getenv("OS_OPENID_SCOPE"),
        "os_client_secret": os.getenv("OS_CLIENT_SECRET"),
        "os_client_id": os.getenv("OS_CLIENT_ID"),
        "os_username": os.getenv("OS_USERNAME"),
        "os_password": os.getenv("OS_PASSWORD"),
        "os_project_domain_id": os.getenv("OS_PROJECT_DOMAIN_ID"),
        "os_project_name": os.getenv("OS_PROJECT_NAME"),
        "os_auth_url": os.getenv("OS_AUTH_URL"),
        "os_region_name": os.getenv("OS_REGION_NAME"),
        "os_interface": os.getenv("OS_INTERFACE"),
        "os_insecure": True,
    }

    VERIFY = None

    if fed_auth.get("os_cacert"):
        VERIFY = fed_auth["os_cacert"]
    elif fed_auth.get("os_insecure") is True:
        VERIFY = False

    # discover OIDC provider token endpoint
    discovery_resp = requests.get(fed_auth["os_discovery_endpoint"], verify=VERIFY)
    token_endpoint = discovery_resp.json()["token_endpoint"]

    # get OIDC access token
    access_req_data = "username={os_username}&password={os_password}&scope={os_openid_scope}&grant_type=password".format(**fed_auth)
    access_resp = requests.post(
        token_endpoint,
        verify=VERIFY,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=access_req_data,
        auth=(fed_auth["os_client_id"], fed_auth["os_client_secret"]),
    )
    access_token = access_resp.json()["access_token"]

    # Exchange OIDC access token for OpenStack Identity unscoped token
    unscoped_token_resp = requests.post(
        "{os_auth_url}/OS-FEDERATION/identity_providers/{os_identity_provider}/protocols/{os_protocol}/auth".format(**fed_auth),
        headers={"Authorization": f"Bearer {access_token}"},
        verify=VERIFY,
    )
    unscoped_token = unscoped_token_resp.headers.get("x-subject-token")

    # (optional) use unscoped token to discover possible authorizaton scopes
    available_project_scopes_resp = requests.get(
        "{os_auth_url}/auth/projects".format(**fed_auth),
        verify=VERIFY,
        headers={"X-Auth-Token": unscoped_token},
    )

    # exchange unscoped token and scope info for scoped token
    scoped_auth_req = {
        "auth": {
            "identity": {
                "methods": [
                    "token"
                ],
                "token": {
                    "id": unscoped_token
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "id": fed_auth["os_project_domain_id"]
                    },
                    "name": fed_auth["os_project_name"]
                }
            }
        }
    }
    scoped_token_resp = requests.post(
        "{os_auth_url}/auth/tokens".format(**fed_auth),
        verify=VERIFY,
        headers={"Content-Type": "application/json"},
        json=scoped_auth_req,
    )
    # more info on user, its roles and groups is in the JSON body of the response
    scoped_token = scoped_token_resp.headers.get("x-subject-token")

    catalog = scoped_token_resp.json()["token"]["catalog"]
    interface = fed_auth.get("os_interface", "public")
    region = fed_auth.get("os_region_name", "RegionOne")

    # discover endpoint of the Image service
    image_service = [s for s in catalog if s["type"] == "image"]
    if not image_service:
        raise Exception("Could not find image service in catalog")
    image_service = image_service[0]
    image_api = [
        e["url"] for e in image_service["endpoints"]
        if e["interface"] == interface and e["region_id"] == region
    ]
    if not image_api:
        raise Exception("Could not find required endpoint for image service")
    image_api = image_api[0].rstrip("/")
    if not image_api.endswith("/v2"):
        image_api += "/v2"

    # use scoped token to make request to image service endpoint
    # list available images
    images_resp = requests.get(
        f"{image_api}/images",
        verify=VERIFY,
        headers={"X-Auth-Token": scoped_token},
    )
    print(images_resp.text)


openstacksdk
------------
and then, the example using ``openstacksdk`` - a dedicated Python API library
for working with OpenStack clouds.
Note that with properly set up ``clouds.yaml``
`configuration file <https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html#config-files>`_
that could've been just 3 lines of code:

.. code-block:: python

    #!/usr/bin/env python
    import os
    import openstack

    fed_auth = {
        "os_auth_type": "v3oidcpassword",
        "os_discovery_endpoint": os.getenv("OS_DISCOVERY_ENDPOINT"),
        "os_identity_provider": os.getenv("OS_IDENTITY_PROVIDER"),
        "os_protocol": os.getenv("OS_PROTOCOL"),
        "os_openid_scope": os.getenv("OS_OPENID_SCOPE"),
        "os_client_secret": os.getenv("OS_CLIENT_SECRET"),
        "os_client_id": os.getenv("OS_CLIENT_ID"),
        "os_username": os.getenv("OS_USERNAME"),
        "os_password": os.getenv("OS_PASSWORD"),
        "os_project_domain_id": os.getenv("OS_PROJECT_DOMAIN_ID"),
        "os_project_name": os.getenv("OS_PROJECT_NAME"),
        "os_auth_url": os.getenv("OS_AUTH_URL"),
        "os_region_name": os.getenv("OS_REGION_NAME"),
        "os_interface": os.getenv("OS_INTERFACE"),
        "os_insecure": True,
    }

    fed = openstack.connect(load_yaml_config=False, **fed_auth)
    # if you save the auth and access info to a clouds.yaml file,
    # https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html#config-files
    # then you don't need env variables, and all the code above can be replaced
    # with single call
    #
    # fed = openstack.connect(cloud=<cloud name>)

    print(fed.list_images())
