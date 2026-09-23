import pytest


@pytest.mark.asyncio
async def test_update_day_boundaries_sets_both(client, test_child, auth_override):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": "06:00", "day_end": "20:00"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["day_start"] == "06:00"
    assert body["day_end"] == "20:00"
    assert len(body["day_start"]) == 5
    assert len(body["day_end"]) == 5


@pytest.mark.asyncio
async def test_get_returns_formatted_day_boundaries(client, test_child, auth_override):
    await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": "06:00", "day_end": "20:00"},
    )

    resp = await client.get("/api/children/")

    assert resp.status_code == 200
    child = next(c for c in resp.json() if c["id"] == test_child.id)
    assert child["day_start"] == "06:00"
    assert child["day_end"] == "20:00"


@pytest.mark.asyncio
async def test_update_only_one_boundary_is_rejected(client, test_child, auth_override):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": "06:00"},
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_one_boundary_with_other_null_is_rejected(
    client, test_child, auth_override
):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": "06:00", "day_end": None},
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_value", ["6:00", "25:00", "06:60", "06:00:00", "0600", "abc"])
async def test_update_invalid_format_is_rejected(
    client, test_child, auth_override, bad_value
):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": bad_value, "day_end": "20:00"},
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("start,end", [("20:00", "06:00"), ("12:00", "12:00")])
async def test_update_start_not_before_end_is_rejected(
    client, test_child, auth_override, start, end
):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"day_start": start, "day_end": end},
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_other_field_leaves_boundaries_untouched(
    client, test_child, auth_override
):
    resp = await client.patch(
        f"/api/children/{test_child.id}",
        json={"name": "renamed baby"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "renamed baby"
    assert body["day_start"] is None
    assert body["day_end"] is None
