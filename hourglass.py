# Libraries
import os
import sys
import calendar
import datetime

import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter.colorchooser import askcolor

class Hourglass:
    """
    Class for the Hourglass application

    Creates a GUI calendar and to-do list application
    """
    def __init__(self):
        """
        Initializes the Hourglass class
        """
        # Constants for time units
        self._NUMBER_MINUTES_IN_HOUR = 60
        self._NUMBER_HOURS_IN_DAY = 24
        self._NUMBER_DAYS_IN_WEEK = 7
        self._NUMBER_MONTHS_IN_YEAR = 12
        self._NUMBER_YEARS = 5

        # Number of weeks (including those with fewer days than the days in week constant above) in a month to display
        self._NUMBER_DISPLAY_WEEKS_IN_MONTH = 6

        # Maximum width of each event on the schedule in screen units
        self._EVENT_LABEL_WRAPLENGTH = 100

        # Constants for on/off values of to-do list task check boxes
        self._TO_DO_LIST_TASK_ON = 1
        self._TO_DO_LIST_TASK_OFF = 0

        # Current moment
        self._now = datetime.datetime.now()

        # Sunday of the week for which events are displayed
        self._displayed_sunday = self._now - datetime.timedelta(days=(self._now.isoweekday() % self._NUMBER_DAYS_IN_WEEK))

        # Currently displayed month and year in the calendar
        self._displayed_month = self._now.month
        self._displayed_year = self._now.year

        # Default mode is dark mode
        self._is_dark_mode = True
        
        # Set colors used by application
        self._set_colors(self._is_dark_mode)
        self._dark_mode_display_text_color = '#c2c2c2'
        self._light_mode_display_text_color = '#4b4b4b'

        # GUI
        self._root = tk.Tk()

        # Font
        self._root.option_add('*Font', 'helvetica')

        # Adjust default GUI size based on screen size
        self._screen_width = self._root.winfo_screenwidth()
        self._screen_height = self._root.winfo_screenheight()
        self._width = int(self._screen_width * 0.7)
        self._height = int(self._screen_height * 0.7)
        self._root.geometry('%sx%s' % (self._width, self._height))
        self._root.update()

        # Adjust minimum and maximum size that GUI can be resized as
        self._root.minsize(int(self._root.winfo_width() * 0.8), int(self._root.winfo_height() * 0.8))
        self._root.maxsize(int(self._root.winfo_width() * 1.2), int(self._root.winfo_height() * 1.2))

        # Row and column weights for widget placement
        self._root.columnconfigure(0, weight=6)
        self._root.columnconfigure(1, weight=1)
        
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=5)

        # Location to find schedule and tasks files
        self._file_location = os.path.dirname('__file__')
        self._schedule_file_location = os.path.join(self._file_location, 'schedule.txt')
        self._to_do_list_file_location = os.path.join(self._file_location, 'tasks.txt')

        # If the files do not exist, create them then open and read; if they do exist, simply open and read
        try:
            if not os.path.exists(self._schedule_file_location):
                with open(os.path.join(self._file_location, 'schedule.txt'), 'x') as opened_file:
                    self._schedule_file = opened_file
            
            with open(os.path.join(self._file_location, 'schedule.txt'), 'r') as opened_file:
                self._schedule_file = opened_file
                self._schedule_read()
            
            if not os.path.exists(self._to_do_list_file_location):
                with open(os.path.join(self._file_location, 'tasks.txt'), 'x') as opened_file:
                    self._to_do_list_file = opened_file
            
            with open(os.path.join(self._file_location, 'tasks.txt'), 'r') as opened_file:
                self._to_do_list_file = opened_file
                self._to_do_read()
        except:
            # Display an error message then exit the application
            self._show_error('unable to read from schedule or to-do list files.')
            sys.exit(1)
        
        # Set up GUI title and GUI widgets
        self._set_title()
        self._week_setup()
        self._event_entry_setup()
        self._calendar_setup()
        self._to_do_setup()
        self._settings_setup()

        # Set the theme
        self._set_theme_mode(change=False)

        # Allow all components of the GUI to be focusable on left click
        self._root.bind_all('<Button-1>', lambda event:event.widget.focus_set())

        self._root.mainloop()

        # If the files do not exist, create them then open and write; if they do exist, simply open and write
        try:
            if not os.path.exists(self._schedule_file_location):
                with open(self._schedule_file_location, 'x') as opened_file:
                    self._schedule_file = opened_file
            
            with open(self._schedule_file_location, 'w') as opened_file:
                self._schedule_file = opened_file
                self._schedule_write()
            
            if not os.path.exists(self._to_do_list_file_location):
                with open(self._to_do_list_file_location, 'x') as opened_file:
                    self._to_do_list_file = opened_file
            
            with open(self._to_do_list_file_location, 'w') as opened_file:
                self._to_do_list_file = opened_file
                self._to_do_write()
        except:
            # Display an error message then exit the application
            self._show_error('unable to write to schedule or to-do list files.')
            sys.exit(1)
    
    def _set_title(self):
        """
        Sets the title of the GUI window; calls itself each second to update
        """
        # Set title using current month and year
        self._now = datetime.datetime.now()
        self._root.title('hourglass  -  ' + calendar.month_name[int(self._now.strftime('%m'))].lower() + self._now.strftime(' %Y'))

        self._root.after(1000, self._set_title)
    
    def _week_setup(self):
        """
        Sets up the week component of the GUI on which events are displayed
        """
        # Frame for all week-related widgets
        self._week_frame = tk.Frame(self._root, borderwidth=0)
        self._week_frame.grid(row=0, column=0, rowspan=2, padx=(6, 3), pady=(6, 3), ipadx=6, ipady=6, sticky='NWSE')
        
        self._week_frame.rowconfigure(0, weight=0)
        self._week_frame.rowconfigure(1, weight=0)
        self._week_frame.rowconfigure(2, weight=1)

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._week_frame.columnconfigure(i, weight=1, uniform='weekday')
        
        # Label indicating which week
        self._week_label = tk.Label(self._week_frame, anchor='w')
        self._week_label.grid(row=0, column=0, columnspan=2, padx=(3, 0), pady=(3, 0), sticky='NWS')

        # Frame for previous, current, and next week buttons
        self._week_buttons_frame = tk.Frame(self._week_frame, borderwidth=0, highlightthickness=0)
        self._week_buttons_frame.grid(row=0, column=4, columnspan=3, sticky='NSE')
        self._week_buttons_frame.columnconfigure(0, weight=1)
        self._week_buttons_frame.columnconfigure(1, weight=2)
        self._week_buttons_frame.columnconfigure(2, weight=1)

        # Button to go to previous week
        self._previous_week_label = tk.Label(self._week_buttons_frame, text='← prev. ', justify='left', borderwidth=0, highlightthickness=0)
        self._previous_week_label.bind('<Button-1>', self._previous_week)
        self._previous_week_label.bind('<ButtonRelease>', self._previous_week_release_button)
        self._previous_week_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current week
        self._current_week_label = tk.Label(self._week_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_week_label.bind('<Button-1>', self._current_week)
        self._current_week_label.bind('<ButtonRelease>', self._current_week_release_button)
        self._current_week_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next week
        self._next_week_label = tk.Label(self._week_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_week_label.bind('<Button-1>', self._next_week)
        self._next_week_label.bind('<ButtonRelease>', self._next_week_release_button)
        self._next_week_label.grid(row=0, column=2, sticky='NWSE')

        # Display week widgets
        self._week_days_labels = []
        self._week_days = []
        self._week_day_separators = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]
        self._week_day_time_references = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            # Label for week day and date
            self._week_days_labels.append(tk.Label(self._week_frame, anchor='w'))

            # Frame for each day
            self._week_days.append(tk.Frame(self._week_frame))
            self._week_days[i].grid(row=2, column=i, sticky='NWSE')
            self._week_days[i].columnconfigure(0, weight=0)
            self._week_days[i].columnconfigure(1, weight=1)

            # Visual differences between first day of week and others
            if i == 0:
                self._week_days_labels[i].grid(row=1, column=i, padx=(3, 0), sticky='NWS')

                # References to indicate time of day (first day of week has time)
                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='00:00', labelanchor='nw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0, relwidth=1, relheight=0.05)
                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='06:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.23, relwidth=1, relheight=0.05)
                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='12:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.48, relwidth=1, relheight=0.05)
                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='18:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.73, relwidth=1, relheight=0.05)
                
            else:
                self._week_days_labels[i].grid(row=1, column=i, sticky='NWS')

                # Separates adjacent days visually
                self._week_day_separators[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
                self._week_day_separators[i][-1].place(relx=0, rely=0, relwidth=0.01, relheight=1)
            
            # References to indicate time of day
            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0, relwidth=1, relheight=0.001)
            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.2459, relwidth=1, relheight=0.001)
            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.4959, relwidth=1, relheight=0.001)
            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.7459, relwidth=1, relheight=0.001)
        
        # Update displayed week to include events
        self._update_week()
    
    def _event_entry_setup(self):
        """
        Sets up the GUI component for entering event information
        """
        self._new_event_calendar = calendar.Calendar(firstweekday=6)

        # Frame for event entry component
        self._event_entry_frame = tk.Frame(self._root, borderwidth=0)
        self._event_entry_frame.grid(row=2, column=0, padx=(6, 6), pady=(3, 3), sticky='NWSE')
        self._event_entry_frame.columnconfigure(0, weight=11)
        self._event_entry_frame.columnconfigure(1, weight=1)
        self._event_entry_frame.columnconfigure(2, weight=0)
        self._event_entry_frame.columnconfigure(3, weight=0)
        self._event_entry_frame.columnconfigure(4, weight=0)
        self._event_entry_frame.columnconfigure(5, weight=0)
        self._event_entry_frame.columnconfigure(6, weight=0)
        self._event_entry_frame.columnconfigure(7, weight=0)
        self._event_entry_frame.columnconfigure(8, weight=0)
        self._event_entry_frame.columnconfigure(9, weight=2)

        # For entering event description
        self._event_entry_variable = tk.StringVar(self._event_entry_frame)
        self._event_entry = tk.Entry(self._event_entry_frame, textvariable=self._event_entry_variable, borderwidth=0, highlightthickness=0)
        self._event_entry.insert(0, ' add new event...')
        self._event_entry.bind('<FocusIn>', self._event_entry_focus)
        self._event_entry.bind('<FocusOut>', self._event_entry_unfocus)
        self._event_entry.bind('<Return>', self._event_entry_enter)
        self._event_entry.grid(row=0, column=0, padx=(0, 3), sticky='NWSE')

        # For selection color
        self._color_selection_label = tk.Label(self._event_entry_frame, text='✏', borderwidth=0, highlightthickness=0)
        self._color_selection_label.bind('<Button-1>', self._choose_color)
        self._color_selection_label.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # For selecting event date; possible days update based on currently selected month
        # For selecting event year
        self._current_event_year = tk.StringVar(self._root)
        self._current_event_year.set(str(self._now.year))
        self._current_event_year.trace('w', self._update_time_date_menu)
        self._dropdown_years = [str(i) for i in range(self._now.year - self._NUMBER_YEARS, self._now.year + self._NUMBER_YEARS + 1)]
        self._year_selection_menu = tk.OptionMenu(self._event_entry_frame, self._current_event_year, *self._dropdown_years)
        self._year_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._year_selection_menu.grid(row=0, column=2, padx=(2, 3), pady=(2, 0),  sticky='NWSE')

        # For selecting event month
        self._current_event_month = tk.StringVar(self._root)
        self._current_event_month.set(str(self._now.month).zfill(2))
        self._current_event_month.trace('w', self._update_time_date_menu)
        self._dropdown_months = [str(i).zfill(2) for i in range(1, self._NUMBER_MONTHS_IN_YEAR + 1)]
        self._month_selection_menu = tk.OptionMenu(self._event_entry_frame, self._current_event_month, *self._dropdown_months)
        self._month_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._month_selection_menu.grid(row=0, column=3, padx=(3, 1), pady=(2, 0),  sticky='NWSE')
        
        # For month/day formatting
        self._date_separator_label = tk.Label(self._event_entry_frame, text='/', justify='center', borderwidth=0, highlightthickness=0)
        self._date_separator_label.grid(row=0, column=4, sticky='NWSE')

        # For selecting event day
        self._current_event_day = tk.StringVar(self._root)
        self._current_event_day.set(str(self._now.day).zfill(2))

        self._dropdown_days = []
        for day in self._new_event_calendar.itermonthdays(self._now.year, self._now.month):
            if day != 0:
                self._dropdown_days.append(str(day).zfill(2))
        
        self._day_selection_menu = tk.OptionMenu(self._event_entry_frame, self._current_event_day, *self._dropdown_days)
        self._day_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._day_selection_menu.grid(row=0, column=5, padx=(1, 3), pady=(2, 0),  sticky='NWSE')

        # For selecting event time
        # For selecting event hour
        self._current_event_hour = tk.StringVar(self._root)
        self._current_event_hour.set(str(self._now.hour).zfill(2))
        self._dropdown_hours = [str(i).zfill(2) for i in range(0, self._NUMBER_HOURS_IN_DAY)]
        self._hour_selection_menu = tk.OptionMenu(self._event_entry_frame, self._current_event_hour, *self._dropdown_hours)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=6, padx=(3, 0), pady=(2, 0),  sticky='NWSE')

        # For hour:minute formatting
        self._time_separator_label = tk.Label(self._event_entry_frame, text=':', justify='center', borderwidth=0, highlightthickness=0)
        self._time_separator_label.grid(row=0, column=7, sticky='NWSE')

        # For selecting event minute
        self._current_event_minute = tk.StringVar(self._root)
        self._current_event_minute.set(str(self._now.minute).zfill(2))
        self._dropdown_minutes = [str(i).zfill(2) for i in range(0, self._NUMBER_MINUTES_IN_HOUR)]
        self._minute_selection_menu = tk.OptionMenu(self._event_entry_frame, self._current_event_minute, *self._dropdown_minutes)
        self._minute_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._minute_selection_menu.grid(row=0, column=8, padx=(1, 0), pady=(2, 0), sticky='NWSE')

        # Bug: entry widgets do not immediately display correctly without text widget on screen
        # Temporary bug fix
        self._placeholder_frame_widget = tk.Label(self._event_entry_frame, borderwidth=0, highlightthickness=0)
        self._placeholder_frame_widget.grid(row=0, column=9)

        self._placeholder_text_widget = tk.Text(self._event_entry_frame, height=1, width=1, takefocus=0, borderwidth=0, highlightthickness=0)
        self._placeholder_text_widget.config({'state': 'disabled'})
        self._placeholder_text_widget.grid(row=0, column=9, in_=self._placeholder_frame_widget)
        self._placeholder_text_widget.lower()

    def _calendar_setup(self):
        """
        Sets up the monthly calendar component of the GUI
        """
        # Frame for the calendar
        self._calendar_frame = tk.Frame(self._root, borderwidth=0)
        self._calendar_frame.grid(row=0, column=1, padx=(3, 6), pady=(6, 3), sticky='NWSE')
        
        self._calendar_frame.rowconfigure(0, weight=1)
        self._calendar_frame.rowconfigure(1, weight=1)

        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH + 1):
            self._calendar_frame.rowconfigure(i + 2, weight=1)

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_frame.columnconfigure(i, weight=1)
        
        # Frame for previous, current, next month buttons
        self._month_buttons_frame = tk.Frame(self._calendar_frame, borderwidth=0, highlightthickness=0)
        self._month_buttons_frame.grid(row=0, column=1, columnspan=5, sticky='NWSE')
        self._month_buttons_frame.columnconfigure(0, weight=1)
        self._month_buttons_frame.columnconfigure(1, weight=2)
        self._month_buttons_frame.columnconfigure(2, weight=1)

        # Button to go to previous month
        self._previous_month_label = tk.Label(self._month_buttons_frame, text='← prev. ', justify='left', borderwidth=0, highlightthickness=0)
        self._previous_month_label.bind('<Button-1>', self._previous_month)
        self._previous_month_label.bind('<ButtonRelease>', self._previous_month_release_button)
        self._previous_month_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current month
        self._current_month_label = tk.Label(self._month_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_month_label.bind('<Button-1>', self._current_month)
        self._current_month_label.bind('<ButtonRelease>', self._current_month_release_button)
        self._current_month_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next month
        self._next_month_label = tk.Label(self._month_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_month_label.bind('<Button-1>', self._next_month)
        self._next_month_label.bind('<ButtonRelease>', self._next_month_release_button)
        self._next_month_label.grid(row=0, column=2, sticky='NWSE')

        # Label for month and year
        self._month_label = tk.Label(self._calendar_frame, justify='center', borderwidth=0)
        self._month_label.grid(row=1, column=0, columnspan=7, sticky='NWSE')

        # Labels for days of the week
        self._calendar_week_days_labels = []

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels.append(tk.Label(self._calendar_frame, justify='right'))
            self._calendar_week_days_labels[-1].grid(row=2, column=i, sticky='NWSE')
        
        # Labels for days of the month
        self._calendar_month_days_labels = [[] for _ in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH)]

        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(self._NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i].append(tk.Label(self._calendar_frame, justify='right'))
                self._calendar_month_days_labels[i][-1].grid(row=i + 3, column=j, sticky='NWSE')
        
        # Update displayed month with dates
        self._update_month()
    
    def _to_do_setup(self):
        """
        Sets up the to-do list component of the GUI
        """
        # Frame for to-do list
        self._to_do_frame = tk.Frame(self._root, borderwidth=0)
        self._to_do_frame.grid(row=1, column=1, padx=(3, 6), pady=(3, 3), ipadx=6, ipady=6, sticky='NWSE')
        self._to_do_frame.grid_propagate(False)

        self._to_do_frame.rowconfigure(0, weight=0)
        self._to_do_frame.rowconfigure(1, weight=0)
        self._to_do_frame.columnconfigure(0, weight=0)

        # Label for title
        self._to_do_label = tk.Label(self._to_do_frame, text='✔︎ to-do list', anchor='w', borderwidth=0, highlightthickness=0)
        self._to_do_label.grid(row=0, column=0, padx=(3, 0), pady=(3, 4), sticky='NWSE')

        # Frame for tasks in to-do list
        self._to_do_list_frame = tk.Frame(self._to_do_frame, borderwidth=0)
        self._to_do_list_frame.grid(row=1, column=0, sticky='NWSE')

        # For entering tasks
        self._to_do_entry_variable = tk.StringVar(self._root)
        self._to_do_entry = tk.Entry(self._root, textvariable=self._to_do_entry_variable, borderwidth=0, highlightthickness=0)
        self._to_do_entry.insert(0, ' add new to-do...')
        self._to_do_entry.bind('<FocusIn>', self._to_do_entry_focus)
        self._to_do_entry.bind('<FocusOut>', self._to_do_entry_unfocus)
        self._to_do_entry.bind('<Return>', self._to_do_entry_enter)
        self._to_do_entry.grid(row=2, column=1, padx=(3, 6), pady=(3, 3), sticky='NWSE')

        # Update to-do list to display tasks
        self._update_to_do()

    def _settings_setup(self):
        """
        Sets up the settings component of the GUI
        """
        # Frame
        self._settings_frame = tk.Frame(self._root, borderwidth=0)
        self._settings_frame.grid(row=3, column=0, padx=(6, 6), pady=(3, 6), sticky='NWSE')
        self._settings_frame.columnconfigure(0, weight=1)
        self._settings_frame.columnconfigure(1, weight=1)
        self._settings_frame.columnconfigure(2, weight=1)
        self._settings_frame.columnconfigure(3, weight=27)

        # For how-to/help
        self._how_to_label = tk.Label(self._settings_frame, text='?', borderwidth=0)
        self._how_to_label.bind('<Button-1>', self._show_how_to)
        self._how_to_label.grid(row=0, column=0, padx=(0, 3), sticky='NWSE')

        # For switching between light/dark mode
        self._theme_mode_label = tk.Label(self._settings_frame, borderwidth=0)
        self._theme_mode_label.bind('<Button-1>', self._set_theme_mode)
        self._theme_mode_label.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

    def _schedule_read(self):
        """
        Reads from schedule file
        """
        self._schedule = {}

        lines = self._schedule_file.readlines()

        for line in lines:
            key = line[:8]
            self._schedule.setdefault(key, []).append(line[8:].rstrip())
        
        self._schedule_file.close()
    
    def _schedule_write(self):
        """
        Writes into schedule file
        """
        self._schedule_file.seek(0)
        self._schedule_file.truncate()

        for key, value in self._schedule.items():
            for item in value:
                self._schedule_file.write(key + item.rstrip() + '\n')
        
        self._schedule_file.close()
    
    def _schedule_add(self, event_date, event_time, event_hex, event_description):
        """
        Adds an event to the schedule

        event_date: Date, yyyymmdd, string
        event_time: Time, hhmm, string
        event_hex: Hex color, string
        event_description: Event description, string
        """
        key = event_date
        self._schedule.setdefault(key, []).append(event_time + event_hex + event_description)
        self._update_week()

    def _schedule_remove(self, event_date, event_time, event_hex, event_description):
        """
        Removes an event from the schedule

        event_date: Date, yyyymmdd, string
        event_time: Time, hhmm, string
        event_hex: Hex color, string
        event_description: Event description, string
        """
        popup = messagebox.askokcancel('remove event?', 'you are about to remove the event "' + event_description + '" at ' + event_time[:2] + ':' + event_time[2:] + ' on ' + event_date[4:6] + '/' + event_date[6:] + '.', icon='warning')

        # Remove if user selects OK
        if popup:
            try:
                key = event_date
                value = self._schedule.get(key)
                event_string = event_time + event_hex + event_description

                if value is not None and event_string in value:
                    del self._schedule[key][value.index(event_string)]
            except:
                self._show_error('no such scheduled event.')
        
        # Update displayed week
        self._update_week()

    def _current_week(self, *args):
        """
        Updates displayed week to reflect the current week
        """
        self._current_week_label.config({'background': self._clicked_widget_color})

        self._now = datetime.datetime.now()
        self._displayed_sunday = self._now - datetime.timedelta(days=(self._now.isoweekday() % self._NUMBER_DAYS_IN_WEEK))
        self._update_week()
    
    def _current_week_release_button(self, *args):
        """
        Restores current week button to unpressed appearance
        """
        self._current_week_label.config({'background': self._widget_color})

    def _previous_week(self, *args):
        """
        Updates displayed week to reflect the previous week
        """
        self._previous_week_label.config({'background': self._clicked_widget_color})
        self._change_week(num=-1)
    
    def _previous_week_release_button(self, *args):
        """
        Restores previous week button to unpressed appearance
        """
        self._previous_week_label.config({'background': self._widget_color})

    def _next_week(self, *args):
        """
        Updates displayed week to reflect the next week
        """
        self._next_week_label.config({'background': self._clicked_widget_color})
        self._change_week(num=1)

    def _next_week_release_button(self, *args):
        """
        Restores next week button to unpressed appearance
        """
        self._next_week_label.config({'background': self._widget_color})
    
    def _change_week(self, num=None, day=None):
        """
        Updates displayed week; accepts either but not both keyword arguments

        num: Number of weeks to change by (negative for previous, positive for next), int
        day: A day in the week to change to, datetime
        """
        if num is not None:
            self._displayed_sunday = self._displayed_sunday + num * datetime.timedelta(days=self._NUMBER_DAYS_IN_WEEK)
        elif day is not None:
            self._displayed_sunday = day - datetime.timedelta(days=(day.isoweekday() % self._NUMBER_DAYS_IN_WEEK))
        
        self._update_week()

    def _update_week(self):
        """
        Updates displayed week and show all scheduled events for that week
        """
        self._displayed_days = ['' for _ in range(self._NUMBER_DAYS_IN_WEEK)]
        self._week_events_labels = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]

        # Date of first day of week
        self._week_label.config(text='week of ' + self._displayed_sunday.strftime('%m/%d') + ', ' + str(self._displayed_sunday.year))

        # Display scheduled events by day
        try:
            for i in range(self._NUMBER_DAYS_IN_WEEK):
                self._clear_day(self._week_days[i])

                self._displayed_days[i] = str((self._displayed_sunday + datetime.timedelta(days=i)).strftime('%Y%m%d'))
                self._week_days_labels[i].config(text=calendar.day_name[(i + self._NUMBER_DAYS_IN_WEEK - 1) % self._NUMBER_DAYS_IN_WEEK].lower() + ' ' + self._displayed_days[i][-2:])
                
                events = self._schedule.get(self._displayed_days[i])

                if events is not None:
                    for item in events:
                        self._week_events_labels[i].append(tk.Label(self._week_days[i], text=item[:2] + ':' + item[2:4] + ' ' + item[11:].rstrip(), justify='left'))
                        self._week_events_labels[i][-1].config({'foreground': self._light_or_dark_mode_text(tuple(int(item[5:11][i:i+2], 16) for i in (0, 2, 4)))})
                        self._week_events_labels[i][-1].config({'background': item[4:11]})
                        self._week_events_labels[i][-1].config({'wraplength': self._EVENT_LABEL_WRAPLENGTH})
                        self._week_events_labels[i][-1].bind('<Button-2>', lambda event, i=i, item=item: self._schedule_remove(self._displayed_days[i], item[:4], item[4:11], item[11:].rstrip()))
                        self._week_events_labels[i][-1].place(relx=0.05, rely=self._fraction_of_day(int(item[:2]), int(item[2:4])))
        except:
            self._show_error('unable to load or update events.')
    
    def _current_month(self, *args):
        """
        Updates displayed month to reflect the current month
        """
        self._current_month_label.config({'background': self._clicked_widget_color})

        self._now = datetime.datetime.now()
        self._displayed_month = self._now.month
        self._displayed_year = self._now.year

        self._update_month()
    
    def _current_month_release_button(self, *args):
        """
        Restores current month button to unpressed appearance
        """
        self._current_month_label.config({'background': self._widget_color})

    def _previous_month(self, *args):
        """
        Updates displayed month to reflect the previous month
        """
        self._previous_month_label.config({'background': self._clicked_widget_color})

        if self._displayed_month == 1:
            self._displayed_month = self._NUMBER_MONTHS_IN_YEAR
            self._displayed_year = self._displayed_year - 1
        else:
            self._displayed_month = self._displayed_month - 1
        
        self._update_month()
    
    def _previous_month_release_button(self, *args):
        """
        Restores previous month button to unpressed appearance
        """
        self._previous_month_label.config({'background': self._widget_color})

    def _next_month(self, *args):
        """
        Updates displayed month to reflect the next month
        """
        self._next_month_label.config({'background': self._clicked_widget_color})

        if self._displayed_month == self._NUMBER_MONTHS_IN_YEAR:
            self._displayed_month = 1
            self._displayed_year = self._displayed_year + 1
        else:
            self._displayed_month = self._displayed_month + 1
        
        self._update_month()

    def _next_month_release_button(self, *args):
        """
        Restores next month button to unpressed appearance
        """
        self._next_month_label.config({'background': self._widget_color})

    def _update_month(self):
        """
        Updates calendar to display selected month
        """
        # Format calendar for display
        calendar_string = calendar.TextCalendar(firstweekday=6).formatmonth(self._displayed_year, self._displayed_month).strip().lower()
        calendar_list = calendar_string.split()

        for i in range(len(calendar_list)):
            if i >= 2 and i <= 8:
                calendar_list[i] = calendar_list[i][0]
        
        for i in range((calendar.monthrange(self._displayed_year, self._displayed_month)[0] + 1) % self._NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(9, '')
        
        while len(calendar_list) < (2 + self._NUMBER_DAYS_IN_WEEK + self._NUMBER_DISPLAY_WEEKS_IN_MONTH * self._NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(len(calendar_list), '')
        
        self._month_label.config({'text': ' '.join(calendar_list[:2])})

        # Labels for days of the month
        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels[i].config({'text': calendar_list[i + 2]})
        
        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(self._NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i][j].config({'text': calendar_list[i * self._NUMBER_DAYS_IN_WEEK + j + 2 + self._NUMBER_DAYS_IN_WEEK]})

                try:
                    day = datetime.datetime(self._displayed_year, self._displayed_month, int(self._calendar_month_days_labels[i][j].cget('text')))
                    self._calendar_month_days_labels[i][j].bind('<Button-1>', lambda event, day=day: self._change_week(day=day))
                except:
                    pass
    
    def _event_entry_focus(self, *args):
        """
        Focuses on the event entry widget, remove prompt text if it is displayed
        """
        if self._event_entry.get() == ' add new event...':
            self._event_entry.delete(1, tk.END)
            
        self._event_entry.config({'foreground': self._entry_text_color})

    def _event_entry_unfocus(self, *args):
        """
        Unfocuses from the event entry widget, restoring prompt text if no text entered
        """
        if self._event_entry.get() == '' or self._event_entry.get() == ' ':
            self._event_entry.delete(0, tk.END)
            self._event_entry.insert(0, ' add new event...')

        self._event_entry.config({'foreground': self._prompt_text_color})
        self._root.focus_set()

    def _event_entry_enter(self, *args):
        """
        When enter is pressed and focus is on the event entry widget, remove focus and add event
        """
        if self._event_entry.get() != ' add new event...':
            self._schedule_add(self._get_event_date(), self._get_event_time(), self._current_event_hex, self._event_entry.get().lstrip())
            self._event_entry.delete(0, tk.END)

        self._event_entry_unfocus()
    
    def _update_time_date_menu(self, *args):
        """
        Updates event day options based on currently selected year and month
        """
        event_year = int(self._current_event_year.get())

        if self._current_event_month.get()[0] == '0':
            event_month = int(self._current_event_month.get()[1])
        else:
            event_month = int(self._current_event_month.get())

        self._dropdown_days = []

        for day in self._new_event_calendar.itermonthdays(event_year, event_month):
            if day != 0:
                self._dropdown_days.append(str(day).zfill(2))
        
        if self._current_event_day.get() not in self._dropdown_days:
            self._current_event_day.set(self._dropdown_days[0])
        
        self._day_selection_menu['menu'].delete(0, tk.END)

        for day in self._dropdown_days:
            self._day_selection_menu['menu'].add_command(label=day, command=lambda value=day: self._current_event_day.set(value))
    
    def _to_do_read(self):
        """
        Reads from to-do list file
        """
        self._to_do_list = []
        lines = self._to_do_list_file.readlines()

        for line in lines:
            self._to_do_list.append(line.rstrip())
        
        self._to_do_list_file.close()

    def _to_do_write(self):
        """
        Writes to to-do list file
        """
        self._to_do_list_file.seek(0)
        self._to_do_list_file.truncate()

        for item in self._to_do_list:
            self._to_do_list_file.write(item.rstrip() + '\n')
        
        self._to_do_list_file.close()

    def _to_do_list_toggle(self, item):
        """
        Toggles the check box for an item

        item: To-do list item, string
        """
        try:
            index = self._to_do_list.index(item)

            if self._to_do_list[index][0] == str(self._TO_DO_LIST_TASK_OFF):
                self._to_do_list[index] = str(self._TO_DO_LIST_TASK_ON) + self._to_do_list[index][1:]
            else:
                self._to_do_list[index] = str(self._TO_DO_LIST_TASK_OFF) + self._to_do_list[index][1:]
        except:
            self._show_error('no such to-do list task.')
        
        self._update_to_do()
    
    def _to_do_list_add(self, item):
        """
        Adds an item to the to-do list

        item: Item to be added, string
        """
        self._to_do_list.append(str(self._TO_DO_LIST_TASK_OFF) + item)

        self._update_to_do()
    
    def _to_do_list_remove(self, item):
        """
        Removes an item from the to-do list

        item: Item to be removed, string
        """
        popup = messagebox.askokcancel('remove task?', 'you are about to remove the task "' + item[1:] + '".', icon='warning')

        # Remove if user selects OK
        if popup:
            try:
                index = self._to_do_list.index(item)
                del self._to_do_list[index]
            except:
                self._show_error('no such to-do list task.')
        
        # Update displayed to-do list
        self._update_to_do()
    
    def _to_do_entry_focus(self, *args):
        """
        Focuses on the to-do entry widget, remove prompt text if it is displayed
        """
        if self._to_do_entry.get() == ' add new to-do...':
            self._to_do_entry.delete(1, tk.END)
            
        self._to_do_entry.config({'foreground': self._entry_text_color})

    def _to_do_entry_unfocus(self, *args):
        """
        Unfocuses from the to-do entry widget, restoring prompt text if no text entered
        """
        if self._to_do_entry.get() == '' or self._to_do_entry.get() == ' ':
            self._to_do_entry.delete(0, tk.END)
            self._to_do_entry.insert(0, ' add new to-do...')

        self._to_do_entry.config({'foreground': self._prompt_text_color})
        self._root.focus_set()

    def _to_do_entry_enter(self, *args):
        """
        When enter is pressed and focus is on the to-do entry widget, remove focus and add to-do
        """
        if self._to_do_entry.get() != ' add new to-do...':
            self._to_do_list_add(self._to_do_entry.get().lstrip())
            self._to_do_entry.delete(0, tk.END)

        self._to_do_entry_unfocus()
    
    def _update_to_do(self):
        """
        Updates to-do list to display current items
        """
        self._to_do_list_display = [[] for _ in range(len(self._to_do_list))]
        self._to_do_list_button_states = [tk.IntVar() for _ in range(len(self._to_do_list))]

        try:
            # Clear displayed items
            self._clear_to_do_list_display()

            # Display all to-do list items
            for i in range(len(self._to_do_list)):
                item = self._to_do_list[i]
                self._to_do_list_button_states[i].set(int(item[:1]))

                self._to_do_list_display.append(tk.Checkbutton(self._to_do_list_frame, text=item[1:], variable=self._to_do_list_button_states[i], onvalue=self._TO_DO_LIST_TASK_ON, offvalue=self._TO_DO_LIST_TASK_OFF, anchor='w', justify='left', command=lambda item=item: self._to_do_list_toggle(item)))
                self._to_do_list_display[-1].config({'foreground': self._label_text_color})
                self._to_do_list_display[-1].config({'background': self._widget_color})
                self._to_do_list_display[-1].config({'highlightthickness': 0})
                self._to_do_list_display[-1].bind('<Button-2>', lambda event, i=i, item=item: self._to_do_list_remove(item))
                self._to_do_list_display[-1].grid(row=i, column=0, padx=(2, 2), sticky='NWSE')
        except:
            self._show_error('unable to load or update to-do list.')
    
    def _choose_color(self, *args):
        """
        Selects color for event
        """
        self._color_selection_dialog = askcolor(title='choose new event color...')
        self._color_selection_label.config({'background': self._color_selection_dialog[1]})
        self._current_event_hex = self._color_selection_dialog[1]
        
        if self._color_selection_dialog[0] is not None:
            (r, g, b) = self._color_selection_dialog[0]
            self._color_selection_label.config({'foreground': self._light_or_dark_mode_text((r, g, b))})

    def _set_theme_mode(self, change=True, *args):
        """
        Sets theme mode for application

        change: Whether to change between light/dark mode, boolean
        """
        if change:
            self._is_dark_mode = not self._is_dark_mode

        if self._is_dark_mode:
            self._theme_mode_label.config(text='☾')
        else:
            self._theme_mode_label.config(text='☼')
        
        self._set_colors(self._is_dark_mode)

        self._change_colors(parent=None)
    
    def _set_colors(self, darkmode):
        """
        Sets colors used by application
        """
        if darkmode:
            # Dark mode colors
            self._prompt_text_color = '#838383'
            self._entry_text_color = '#c2c2c2'
            self._label_text_color = '#c2c2c2'
            self._menu_text_color = '#ebebeb'
            self._background_color = '#2c2c2c'
            self._widget_color = '#383838'
            self._clicked_widget_color = '#2e2e2e'
            self._faint_text_color = '#494949'
            self._faint_display_color = '#424242'
        else:
            # Light mode colors
            self._prompt_text_color = '#797979'
            self._entry_text_color = '#4b4b4b'
            self._label_text_color = '#4b4b4b'
            self._menu_text_color = '#505050'
            self._background_color = '#d3d3d3'
            self._widget_color = '#b3b3b3'
            self._clicked_widget_color = '#969696'
            self._faint_text_color = '#a5a5a5'
            self._faint_display_color = '#a1a1a1'
    
    def _change_colors(self, parent=None):
        """
        Changes colors for widget and all descendant widgets based on current theme mode

        parent: Widget to change color for, tkinter widget
        """
        # If no widget provided, start at root
        if parent is None:
            parent = self._root
            parent.config({'background': self._background_color})
        
        # Change color for all descendant widgets
        for child in parent.winfo_children():
            if child.winfo_children():
                self._change_colors(parent=child)
            
            if child is self._placeholder_frame_widget or child is self._placeholder_text_widget:
                child.config({'foreground': self._background_color})
                child.config({'background': self._background_color})

            elif type(child) is tk.Label and parent not in self._week_days:
                if child is self._time_separator_label or child is self._date_separator_label:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._background_color})
                else:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._widget_color})

                    if child is self._color_selection_label:
                        self._current_event_hex = child.cget('background')
            
            elif type(child) is tk.Entry:
                child.config({'foreground': self._prompt_text_color})
                child.config({'background': self._widget_color})
            
            elif type(child) is tk.LabelFrame:
                child.config({'foreground': self._faint_text_color})
                child.config({'background': self._widget_color})
            
            elif type(child) is tk.OptionMenu:
                child.config({'foreground': self._menu_text_color})
                child.config({'background': self._background_color})
            
            elif type(child) is tk.Checkbutton:
                child.config({'foreground': self._label_text_color})
                child.config({'background': self._widget_color})

            elif type(child) is tk.Frame:
                if child in [self._week_frame, self._week_buttons_frame, self._calendar_frame, self._month_buttons_frame, self._to_do_frame] or child is self._to_do_list_frame or child in self._week_days:
                    child.config({'background': self._widget_color})
                elif any(child in element for element in self._week_day_time_references):
                    child.config({'background': self._faint_display_color})
                else:
                    child.config({'background': self._background_color})
    
    def _clear_day(self, parent):
        """
        Clears displayed events of a day

        parent: The day to clear, tk.Frame
        """
        for child in parent.winfo_children():
            # Do not clear visual, non-event elements
            if not any(child in element for element in self._week_day_time_references) and not any(child in element for element in self._week_day_separators):
                child.destroy()
    
    def _clear_to_do_list_display(self):
        """
        Clears displayed to-do list items
        """
        for child in self._to_do_list_frame.winfo_children():
            child.destroy()
    
    def _fraction_of_day(self, h, m):
        """
        Returns the fraction of the day corresponding to the given time

        h: Hour, int
        m: Minute, int
        return: Fraction of the day, float
        """
        return (h * 60 + m) / (24 * 60)

    def _light_or_dark_mode_text(self, rgb):
        """
        Returns the text color to be used on the given background color

        rgb: Given background color, tuple
        return: Text color to be used as a hex color, string
        """
        r, g, b = rgb
        
        # Formula from alienryderflex.com/hsp.html
        if (0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2) > 16256:
            return self._light_mode_display_text_color
        else:
            return self._dark_mode_display_text_color
    
    def _get_event_date(self):
        """
        Returns the current event date entered

        return: Event date, yyyymmdd, string
        """
        return self._current_event_year.get() + self._current_event_month.get() + self._current_event_day.get()

    def _get_event_time(self):
        """
        Returns the current event time entered

        return: Event time, hhmm, string
        """
        return self._current_event_hour.get() + self._current_event_minute.get()
    
    def _show_how_to(self, *args):
        """
        Displays how-to message
        """
        msg = messagebox.showinfo('your hourglass', 'press enter to add event/task\nright click to remove\n\nclick on days in monthly calendar to display events for that week\n\nsun/moon → light/dark mode\npencil → custom event color')
    
    def _show_error(self, message):
        """
        Displays error with given message

        message: Error message, string
        """
        msg = messagebox.showerror('hourglass error', message)

if __name__ == '__main__':
    Hourglass()