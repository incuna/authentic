.. _administration_with_policies:

=========================================================
How global policies are used in Authentic2 administration
=========================================================

The policy management with global policies is nearly used for any kind of
policy in Authentic2.

For each kind of these policies, the system takes in account two special
global policies named 'Default' and 'All':

 * If no other policy applies, the policy 'Default' will apply.

 * A policy can be created and attached to any related object. This policy is authoritative on policy 'Default'.

 * If the policy 'All' exists, it is authoritative on any other policy.

 * The global policies must be created by the administrator if necessary.

**A policy is taken in account only if it is enabled.**

**When a regular policy is associated with an object, it is taken in account
only if the option 'enable the following policy' is checked.**

::

    def get_sample_policy(any_object):
        # Look for a global policy 'All'
        try:
            return SamplePolicy.objects.get(name='All', enabled=True)
        except SamplePolicy.DoesNotExist:
            pass
        # Look for a regular policy
        if any_object.enable_following_sample_policy:
            if any_object.sample_policy:
                return any_object.sample_policy
        # Look for a global policy 'Default'
        try:
            return SamplePolicy.objects.get(name='Default', enabled=True)
        except SamplePolicy.DoesNotExist:
            pass
        return None

*It is advised to add a 'Default' global policy when it is expected to apply a
policy to all related objects. Add e regular policy to some objects are then
used to handle particular configurations.*

*A 'Default' global policy should be defined to avoid misonfiguration.*

*A 'All' global policy should be used to enforce a global configuration for
all related objects or for testing purposes.*
