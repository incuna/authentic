.. _sync-metadata_script:

===========================================================================================================
How to create/import and delete in bulk SAML2 identity and service providers with the sync-metadata script?
===========================================================================================================

This section explains hot to use the script sync-metadata.

Presentation
============

This script allows to create/import and deleted in bulk SAML2 identity and
service providers using standard SAML2 metadata files containing entity
descriptors.

An example of such a file used in production is the global metadata file of
the identity federation of French universities that can be found at http://...

Use the following command::

    path_to_project/authentic2$ python manage.py sync-metadata file_name [options]

Options
=======

* idp

    Load only identity providers of the metadata file.

* sp

    Load only service providers of the metadata file.

* source

    Used to tag all imported providers with a label. This option is used to
    metadata reloading and deletion in bulk.

    Reloading a metadata file, when a provider with same entity is found, it is
    updated. If a provider in the metadata file does not exist it is created.
    If a provider exists in the system but not in the metadata file, it is
    removed.

    **For reloading, a source can only be associated with a unique metadata
    file. This is due to the fact that all providers of a source not found in
    the metadata file are removed.**

::

    path_to_project/authentic2$ python manage.py sync-metadata file_name --source=french_federation

* sp-policy

    To configure the SAML2 parameters of service providers imported with the
    script, a policy of type SPOptionsIdPPolicy must be created in the
    the administration interface.
    Either it is a global policy 'Default' or 'All' or it is a regular policy.
    If it is a regular policy, the policy name can be specified in parameter
    of the script with this option.
    The policy is then associated to all service providers created.

::

    path_to_project/authentic2$ python manage.py sync-metadata file_name --sp-policy=sp_policy_name

* idp-policy

    To configure the SAML2 parameters of identity providers imported with the
    script, a policy of type IdPOptionsSPPolicy must be created in the
    the administration interface.
    Either it is a global policy 'Default' or 'All' or it is a regular policy.
    If it is a regular policy, the policy name can be specified in parameter
    of the script with this option.
    The policy is then associated to all service providers created.

::

    path_to_project/authentic2$ python manage.py sync-metadata file_name --idp-policy=idp_policy_name

* delete

    With no options, all providers are deleted.

    With the source option, only providers with the source name given are deleted.

    **This option can not be combined with options idp and sp.**

* ignore-errors

    If loading of one EntityDescriptor fails, continue loading
