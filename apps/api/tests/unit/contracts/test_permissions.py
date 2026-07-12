from app.contracts.permissions import ALL_PERMISSIONS, Permission


def test_permissions_are_unique() -> None:
    assert len(ALL_PERMISSIONS) == len(Permission)


def test_permissions_use_resource_action_format() -> None:
    for permission in Permission:
        resource, separator, action = permission.value.partition(":")
        assert separator == ":"
        assert resource.islower()
        assert action.islower()
        assert resource
        assert action
