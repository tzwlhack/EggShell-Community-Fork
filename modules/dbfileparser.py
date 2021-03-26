import sqlite3

def parse_safari_history_db(safari_history_db: str):
    """Parses the contents of a Safari History database file and returns a

    Args:
        safari_history_db (str): Path to a History.db database file

    Returns:
        dict: Dictionary containing the most important data
    """
    
    db = sqlite3.connect(safari_history_db)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('''SELECT 
            history_item as lookup_id,
            title,
            load_successful as open_successfull,
            datetime(visit_time + 978307200, 'unixepoch', 'localtime') as 'date'
        FROM history_visits''')
    result_temp_dict = list(map(dict,cursor.fetchall()))
    for item in result_temp_dict:
        cursor.execute( '''SELECT 
                url,
                domain_expansion,
                visit_count
            FROM history_items
            WHERE id = {item_id}'''.format(item_id=item["lookup_id"]))
        current_row_dict = list(map(dict,cursor.fetchall()))
        item["details"] = current_row_dict
        del item["lookup_id"]
    return result_temp_dict

def parse_safari_bookmarks_db(safar_bookmarks_db : str):
    """Parses the contents of a Safari Bookmarks database file

    Args:
        safar_bookmarks_db (str): Path to a Bookmarks.db database file

    Returns:
        dict: Dictionary containing the most importent data
    """

    db = sqlite3.connect(safar_bookmarks_db)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('''SELECT
            title,
            url
        FROM bookmarks
        WHERE num_children = 0
        AND url <> "" ''')
    return list(map(dict,cursor.fetchall()))

def parse_chat_convo(sms_db : str, partner : str, imessage : bool):
    """Parses the contents of a SMS database file

    Args:
        sms_db (str): Path to a SMS.db database file
        partner (str): Email/mobile number of the conversation partner
        imessage (bool): Dump iMessage chat

    Returns:
        dict: Dictionary containing the chat data
    """

    db = sqlite3.connect(sms_db)
    result_arr = {
        "protocol": "{}".format('iMessage' if imessage == True else 'SMS'),
        "partner": partner,
        "success": True,
        "data": []
    }
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('''SELECT
            ROWID
        FROM chat
        WHERE guid LIKE '{protocol};%;{partner}' 
        '''.format(partner=partner, protocol=('iMessage' if imessage == True else 'SMS')))
    try:
        rowid_chat = list(map(dict,cursor.fetchall()))[0]["ROWID"]
    except IndexError:
        result_arr["success"] = False
        return result_arr
    cursor.execute('''SELECT
            message_id
        FROM chat_message_join
        WHERE chat_id = {row_id}
        '''.format(row_id=rowid_chat))
    message_id_arr = [int(item[0]) for item  in list(map(list, cursor.fetchall()))]
    for message_id in message_id_arr:
        cursor.execute('''SELECT
                ROWID as 'message_id',
                text,
                date as 'timestamp',
                is_from_me
            FROM message
            WHERE ROWID = {message_id}
            AND text <> ""
            ORDER BY date
            '''.format(message_id=message_id))
        message_element_arr = list(map(dict, cursor.fetchall()))[0]
        result_arr["data"].append(message_element_arr)
    return result_arr