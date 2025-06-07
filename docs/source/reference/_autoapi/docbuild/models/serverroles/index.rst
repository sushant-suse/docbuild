docbuild.models.serverroles
===========================

.. py:module:: docbuild.models.serverroles

.. autoapi-nested-parse::

   Server roles for the docbuild application.



Classes
-------

.. autoapisummary::

   docbuild.models.serverroles.ServerRole


Module Contents
---------------

.. py:class:: ServerRole

   Bases: :py:obj:`enum.StrEnum`


   The server role.


   .. py:attribute:: PRODUCTION
      :value: 'production'


      Server is in production mode, serving live traffic.



   .. py:attribute:: PROD


   .. py:attribute:: P


   .. py:attribute:: production


   .. py:attribute:: prod


   .. py:attribute:: p


   .. py:attribute:: STAGING
      :value: 'staging'


      Server is in staging mode, used for testing before production.



   .. py:attribute:: STAGE


   .. py:attribute:: S


   .. py:attribute:: staging


   .. py:attribute:: stage


   .. py:attribute:: s


   .. py:attribute:: TESTING
      :value: 'testing'


      Server is in testing mode, used for development and QA.



   .. py:attribute:: TEST


   .. py:attribute:: T


   .. py:attribute:: testing


   .. py:attribute:: test


   .. py:attribute:: t


