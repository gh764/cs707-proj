import sqlite3

connection = sqlite3.connect('./database')
c = connection.cursor()

# usr table. 
c.execute('''
    create table if not exists [usr] (
	[uid]	    [int]    not null   primary key,
	[passwd]    [text]   not null
    )
''')

# points-of-interest table. 
c.execute('''
    create table if not exists [poi] (
    	[pid]		[integer]	    primary key,
	[uid]		[int]	not null    references [usr]([uid]),
	[name]		[text]	not null,
	[description]	[text],
	[longitude]	[int]	not null, 
	[latitude]	[int]	not null,
	[altitude]	[int],
	[radius]	[int]	not null    check(radius > 0)
    )
''')

# model table.
# sections
# $1: model identifier & owner.
# $2: model type.
# $3: version & modification information 
# $4: data collection and aggregration information.
# $5: model statistics 
# $6: triggers which cause the model to be rebuilt at
#     earliest rebuild date. trigger-value of 0 disables trigger. 
c.execute('''
    create table if not exists [model] (
	[mid]	                [integer]                       primary key,
        [uid]                   [int]   not null                unique references [usr]([uid]),

        [schedule]              [char]  not null    default 'r' check([schedule] in ('r', 'i')),
        [type]                  [char]  not null    default 's' check([type] in ('c', 's')),

        [version]               [int]   not null    default 0,
        [created_on]            [date]  not null    default current_date,
        [last_updated_on]       [date]  not null    default current_date,
        [earliest_rebuild]      [int]   not null    default 7,
        [expires_in]            [int]   not null    default 90,

        [window_size]           [int]   not null    default 2   check([window_size] >= 2 and [window_size] <= 24),
        [agg_fx]                [char]  not null    default 'a' check([agg_fx] in ('a', 'w')),
        [granularity]           [int]   not null    default 15  check([granularity] > 0 & [granularity] < 120),

        [nr_matches]            [int]   not null    default 0,
        [nr_successful]         [int]   not null    default 0,
        [streak]                [int]   not null    default 0,
        [last10]                [int]   not null    default 0,

        [rebuild]               [int]   not null    default 0   check([rebuild] = 0 or [rebuild] = 1),
        [total_mismatch_trig]   [real]  not null    default 0.5 check([total_mismatch_trig] >= 0 and [total_mismatch_trig] <= 1),
        [losing_strk_trig]      [int]   not null    default 5   check([losing_strk_trig] >= 0),
        [last10_lsng_strk_trig] [real]  not null    default 0.5 check([last10_lsng_strk_trig] >= 0 and [last10_lsng_strk_trig] <= 1),

        unique([mid], [uid])
    )
''')

# create subscriber table. 
c.execute('''
    create table if not exists [subscriber] (
	[sid]	        [integer]           primary key,
	[uid]	        [int]   not null    references [usr]([uid]),
        [name]          [text]  not null,
        [enbl_alrts]    [int]   not null    default 0
    )
''')

# create location_snapshot table. 
c.execute('''
    create table if not exists [location_snapshot] (
	[uid]	    [int]	not null,
	[location]  [int]	not null,
	[arrival]   [datetime]	not null,
	[departure] [datetime]  not null,

	foreign key([uid], [location]) references [poi](uid, pid)
    )
''')

# agg_location_snapshot table.
c.execute('''
    create table if not exists [agg_location_snapshot] (
        [mid]           [int]   not null,    
        [version]       [int]   not null,

        [day]           [int]   not null    check([day] in (0,1,2,3,4,5,6)),
        [start]         [int]   not null,
        [end]           [int]   not null,
        [cxl_thrshld]   [int]               default 15,
        [location]      [int]               references [poi](pid),
        
        foreign key([mid], [version]) references [model]([mid], [version])
    )
''')

# alert table.
c.execute('''
    create table if not exists [alert] (
        [aid]           [integer]                       primary key,
        [sid]           [int]   not null                references [subscriber]([sid]),

        [event]         [char]  not null                check([event] in ('a', 'd')),
        [location]      [int]   not null                references [poi]([pid]),
        [send_within]   [int],

        [is_enabled]    [int]   not null    default 0
    )
''')

c.close()
connection.commit()
connection.close()
