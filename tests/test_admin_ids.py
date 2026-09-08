from admin_ids import parse_admin_ids, sender_is_admin


def test_sender_is_admin_when_user_id_is_listed():
    admin_ids = parse_admin_ids("111, 222")
    assert sender_is_admin(user_id="222", chat_id="999", admin_ids=admin_ids)


def test_sender_is_admin_when_chat_id_is_listed():
    admin_ids = parse_admin_ids("111, 222")
    assert sender_is_admin(user_id="999", chat_id="111", admin_ids=admin_ids)


def test_sender_is_not_admin_when_neither_id_matches():
    admin_ids = parse_admin_ids("111, 222")
    assert not sender_is_admin(user_id="1", chat_id="2", admin_ids=admin_ids)


def test_sender_is_not_admin_when_list_is_empty():
    assert not sender_is_admin(
        user_id="111", chat_id="111", admin_ids=frozenset()
    )
