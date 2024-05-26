################################################################
Authentication flow with Keystone and OpenID Connect - with cURL
################################################################

.. |date| date::

:date: 2021-04-30
:modified: |date|
:tags: openstack,keystone,federation,openid,oidc,curl
:category: work
:slug: keystone-oidc-curl
:lang: en
:authors: pas-ha
:summary: auth to keystone federated via oidc with cURL calls
:status: draft


Recently I was tasked to provide an example curl commands to realize the
authentication process required to get an OpenStack Identity (Keystone) token
for a user federated via OpenID Connect.
While usually we tend to use already established libraries like
``keystoneauth`` or ``openstacksdk`` for that, but since I not so long ago
had to dive into OpenID Connect anyway, this posed  an interesting task.

I use
`Mirantis OpenStack for Kubernetes <https://www.mirantis.com/software/mirantis-openstack-for-kubernetes/>`_
(naturally :-) ), that integrates
Keystone with Keycloak via OpenID Connect, OpenStack release is Victoria.


Pre-requisites
==============

- OpenStack deployed and configured to use federation via OpenID Connect.
- Account in the Identity Provider allowing you to login to OpenStack.
- `v3oidcpassword <https://docs.openstack.org/keystoneauth/latest/authentication-plugins.html#federation>`_
  authenticationauthentication enabled and working
- ``curl`` and ``jq`` installed and available

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
  Name of the identity provider configured in Keystone

OS_PROTOCOL
  Name of the protocol configured for this Identity Provider in Keystone

OS_CLIENT_ID
  The client name to use when contacting Identity Provider
  Note - this is NOT your OpenStack login

OS_CLIENT_SECRET
  The password to use for the Identity Provider client.
  Usually it must be kept secret,
  as in standard Web SSO application of OpenID Connect,
  but here, as with Kubernetes + OpenID Connect,
  the CLI client is required to know it.
  Some Identity Providers allow to create clients without secrets (for example
  Keycloak does).

OS_OPENID_SCOPE
  The scope to use for authentication, governs how much info about you the
  Identity Provider will pass to the Service Provider - in this case you :-)
  At least (and usually only) must be ``openid``.

OS_USERNAME
  Your username with Identity Provider you want to login to OpenStack with

OS_PASSWORD
  Your password for your account with the Identity Provider.

OS_PROJECT_NAME
  The name of the OpenStack project you want to authenticate to.

OS_PROJECT_DOMAIN_ID
  ID of the OpenStack Identity domain that project belongs to.

Get it from Horizon
~~~~~~~~~~~~~~~~~~~
The easiest way to obtain those is to login via federation to Horizon,
and download the RC file from the UI

<INSERT IMAGE HERE>

source this file into the active shell, it will ask you for your password

.. code-block:: bash

   source .sh

Authentication Flow
===================

Now let's start with curl-ing. I use ``-sk`` to silence the progress indicator
and, since I use development toy environment and self-signed TLS certificates,
ignore TLS verification failures.

I am following the calls that would've been made when using ``keystoneauth``
library with ``v3oidcpassword`` authentication type.


Get OIDC token endpoint
-----------------------

Using the discovery endpoint, find the URL of token endpoint

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

The trick is the Content-Type - as per The
`OpenID Connect RFC <https://openid.net/specs/openid-connect-core-1_0.html#TokenRequest>`_
this is how it must be done with Form Serialization, not JSON.

The client id and client secret are used for HTTP Basic Authentication, again,
as per that RFC.

Get the unscoped Keystone token
-------------------------------

Now the OpenStack part. In OpenStack, tokens are issued and valid in various
"scopes" - project, domain, system or unscoped.

With federation, API user is expected to first exchange the Identity Provider
token for unscoped OpenStack Identity token.

.. code-block:: bash

   unscoped_token=$(curl -sik \
       -I \
       -X POST $OS_AUTH_URL/OS-FEDERATION/identity_providers/${OS_IDENTITY_PROVIDER}/protocols/${OS_PROTOCOL}/auth \
       -H "Authorization: Bearer $access_token" \
       | grep x-subject-token \
       | awk '{print $2}' \
       | tr -d '\r')

Here already we have some inconveniences with Bash:
the token arrives in the header, but the response body (json) also has some useful info
we are ignoring it but it may become useful in some applications
result of grep + awk has new line in the end, need to trim it to put into JSON

Prepare JSON for scoped token request
-------------------------------------

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

Generating JSON in Bash is very awkward due to double-quotes
and lots of escaping...
just save the request JSON body to file (obviously not secure)

Get scoped token
----------------

Biggest disadvantages here, as again, the token is in the headers,
but the response body contains a lot of useful info, including auth info
(UUIDs of project, domain etc, group assignments, roles if explicit,
plus the Identity Catalog that may be needed to discover the actual URL
of the service we want to acces with the received token
Again, we skip all that useful info and only fetch the token

.. code-block:: bash

   scoped_token=$(curl -sik \
       -X POST $OS_AUTH_URL/auth/tokens \
       -d "@$token_request" -H "Content-Type: application/json" \
       | grep x-subject-token \
       | awk '{print $2}' \
       | tr -d '\r')


Remove the temporary file with token request body, tiny security improvement

.. code-block:: bash

   rm $token_request

Use scoped token to make request to an OpenStack service
========================================================
Here hardcoded endpoint is used, however base part of it could've
been discovered from the response body of the previous request
I specifically use Glance in the example as it has no project UUID in the
endpoint, but many more services will need that.

.. code-block:: bash

   curl -sk \
       -X GET https://glance.it.just.works/v2/images \
       -H "X-Auth-Token: $scoped_token" \
       | jq .images
