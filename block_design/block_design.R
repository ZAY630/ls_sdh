# Block design for DBC




#### Setup ####
# use pacman
require(pacman)

# load libraries
pacman::p_load(tidyverse, lubridate, here, scales, slider, patchwork, # general
               broom, ggpmisc, ggpubr, # linear models
               RMV2.0, # TOWT model
               sprtt, effsize) # sequential testing

# turn off scientific notation
options(scipen = 999)




#### Experimental Design 1 ####
# 2 strategies: Baseline (reset based on outdoor temperature); Intervention (performance optimization)
# experimental unit: 3 days as a unit to prevent carryover effect
# block by time of week
# set number of weeks and seasons for field study

params_block <- list(current_seed = 94530, # set first seed
                     nos_try = 0, # number of tries
                     max_try = 1000, # maximum number of tries
                     n_weeks = 8,
                     n_seasons = 1,
                     chunk = 1, 
                     max_consecutive_criteria = 4, # consecutive if more than X days. stops. 9 for chunk == 3, 12 for chunk == 4
                     max_margin_criteria = 2, # 4 for chunk == 3, 3 for chunk == 4
                     success = TRUE)

while (params_block$success){
  # do block design
  df_blocks <- blocksdesign::blocks(treatments = 2, # 2 intervention strategies, 1 control strategy
                                    replicates = floor(params_block$n_weeks * 7 / params_block$chunk / 2), # 2 strategies, 3 days as a randomization unit
                                    blocks = params_block$n_seasons, # 7 weekdays
                                    searches = 20, 
                                    jumps = 1,
                                    seed = params_block$current_seed)
  
  # build timeseries and assign strategies
  df_blocks <- df_blocks[["Design"]] %>%
    # tibble() function creates a dataframe
    tibble() %>%
    select(season = Level_1, strategy = treatments) %>%
    arrange(season) %>%
    mutate(season = as.numeric(str_remove_all(season, "B"))) %>%
    slice(rep(row_number(), each = params_block$chunk)) %>%
    mutate(date = ymd('2024-01-15') + days(row_number()-1),
           weekday = wday(date, label = TRUE)) %>%
    select(season, date, weekday, strategy)
  
  # count consecutive days
  df_cons <- df_blocks %>%
    select(strategy) %>%
    mutate(strategy = as.numeric(as.character(strategy)),
           consec = ifelse(lag(strategy) == strategy, FALSE, TRUE),
           consec = replace_na(consec, FALSE),
           cumul = cumsum(consec)) %>%
    group_by(cumul) %>%
    mutate(row_number = row_number()) %>%
    ungroup()
  
  # get count by weekday
  df_wdays <- df_blocks %>%
    group_by(weekday = wday(date),
             strategy) %>%
    count()
  
  # determine the max value
  #consecutive_max <- max(df_cons$row_number, na.rm = TRUE)
  
  # find the maximum consecutive repeat if more than max_consecutive_criteria days, stop if not
  if(max(df_cons$row_number, na.rm = TRUE) > params_block$max_consecutive_criteria) {
    print(paste0("Highest consecutive days is ", max(df_cons$row_number, na.rm = TRUE) ,
                 ", trying again. Current seed is ", params_block$current_seed))
    
    # generate new seed
    params_block$current_seed <- sample(1:2^15, 1)
    
    # set seed
    set.seed(params_block$current_seed)
    
    # update counter
    params_block$nos_try <- params_block$nos_try + 1
    
    # check the number of tries
    if (params_block$nos_try >= params_block$max_try){
      params_block$success <- FALSE
      print('Reached the max number of tries. Please try changing the parameters.')
    }
    
  } else if (max(df_wdays$n) - min(df_wdays$n) > params_block$max_margin_criteria) {
    print(paste0("Highest margin between weekdays is ", max(df_wdays$n) - min(df_wdays$n),
                 ", trying again. Current seed is ", params_block$current_seed))
    
    # generate new seed
    params_block$current_seed <- sample(1:2^15, 1)
    
    # set seed
    set.seed(params_block$current_seed)
    
    # update counter
    params_block$nos_try <- params_block$nos_try + 1
    
    # check the number of tries
    if (params_block$nos_try >= params_block$max_try){
      params_block$success <- FALSE
      print('Reached the max number of tries. Please try changing the parameters.')
    }
  } else {
    
    print(paste0("Success! Highest consecutive days is ", max(df_cons$row_number, na.rm = TRUE), "."))
    print(paste0("Success! Highest margin weekdays is ", max(df_wdays$n) - min(df_wdays$n), "."))
    params_block$success <- FALSE
    
    return(df_blocks)
    
  }
}





#### Check balance ####
# get count by strategy
df_blocks %>% 
  group_by(season, strategy) %>% 
  count() %>% 
  ungroup()

# get count by weekday
df_blocks %>%
  group_by(weekday = wday(date),
    strategy) %>%
  count()
  
# summarise consecutive strategies
df_blocks %>%
  # lag calculate the difference between current value and previous value
  # returns 1 when two consecutive same strategy, 0 when strategy changes
  mutate(consec = ifelse(lag(strategy, 1) == strategy, 1, 0)) %>%
  group_by(strategy) %>%
  summarise(consecutive = sum(consec, na.rm = TRUE)) %>% 
  ungroup()

df_blocks %>% 
  ggplot() +
  geom_col(aes(x = date, y = as.numeric(strategy), group = 1), position = "dodge")

# save
write_csv(df_blocks, here(str_glue("block_{params_block$chunk}_schedule_SDH.csv")))


