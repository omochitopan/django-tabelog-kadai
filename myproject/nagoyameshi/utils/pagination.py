def pagination(per_page, current_num, total_num):
    page_list = []
    if current_num == 1:
        page_list.append(1)
    elif current_num <= per_page + 1:
        for num in range(1, current_num + 1):
            page_list.append(num)
    else:
        page_list.append(1)
        page_list.append("...")
        for num in range(current_num - per_page, current_num + 1):
            page_list.append(num)
    if current_num >= total_num - per_page:
        if current_num != total_num:
            for num in range(current_num + 1, total_num + 1):
                page_list.append(num)
    else:
        for num in range(current_num + 1, current_num + 6):
            page_list.append(num)
        page_list.append("...")
        page_list.append(total_num)
    return page_list
