def set_format_date_time_field(date_time_field):
    date_time_field.input_formats = ['%d-%m-%Y %H:%M']
    date_time_field.widget.format = '%d-%m-%Y %H:%M'


def set_format_date_field(date_field):
    date_field.input_formats = ['%d-%m-%Y']
    date_field.widget.format = '%d-%m-%Y'
