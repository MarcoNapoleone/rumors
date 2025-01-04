from flask import current_app


def get_balanced_ab_group():
    with current_app.app_context():
        users = current_app.db.users
        test_group_a = users.count_documents({'test_group': 'A'})
        test_group_b = users.count_documents({'test_group': 'B'})

        if test_group_a == test_group_b:
            return 'A'
        elif test_group_a < test_group_b:
            return 'A'
        else:
            return 'B'
