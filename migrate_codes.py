import sqlite3

def run_migration():
    conn = sqlite3.connect('instance/jig.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT id, code FROM challenges WHERE code LIKE 'JIG-%'")
    rows = cursor.fetchall()
    print(f'Found {len(rows)} challenges with JIG- prefix')
    for r in rows:
        new_code = r[1].replace('JIG-', 'SS-')
        cursor.execute('UPDATE challenges SET code = ? WHERE id = ?', (new_code, r[0]))

    cursor.execute("SELECT id, message FROM notifications WHERE message LIKE '%JIG-%'")
    notifs = cursor.fetchall()
    print(f'Found {len(notifs)} notifications with JIG- prefix')
    for n in notifs:
        new_msg = n[1].replace('JIG-', 'SS-')
        cursor.execute('UPDATE notifications SET message = ? WHERE id = ?', (new_msg, n[0]))

    cursor.execute("SELECT id, notes FROM status_history WHERE notes LIKE '%JIG-%'")
    notes = cursor.fetchall()
    print(f'Found {len(notes)} status_history with JIG- prefix')
    for h in notes:
        new_n = h[1].replace('JIG-', 'SS-')
        cursor.execute('UPDATE status_history SET notes = ? WHERE id = ?', (new_n, h[0]))

    conn.commit()
    conn.close()
    print('Migration completed successfully!')

if __name__ == '__main__':
    run_migration()
