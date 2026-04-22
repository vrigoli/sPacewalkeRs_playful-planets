# NASA Spacewalk Analysis — R
# https://data.nasa.gov/resource/eva.json (with modifications)
# Generates three figures for the manuscript

library(jsonlite)
library(dplyr)
library(ggplot2)
library(lubridate)
library(tidyr)

output_dir <- '/home/sarah/Projects/spacewalk-analysis/results/figures/'

df <- fromJSON("data/data.json", flatten = TRUE)
df$date <- as.Date(df$date)
df$year <- year(df$date)
df$country <- trimws(df$country)

parse_duration <- function(d) {
  # Convert "H:MM" string to total minutes
  parts <- strsplit(d, ":")[[1]]
  as.integer(parts[1]) * 60L + as.integer(parts[2])
}

# df$duration_mins <- sapply(df$duration, parse_duration)

colour_map <- c("USA" = "#377eb8", "Russia" = "#ff7f00")

# --------------------------------------------------
# Figure 1: Annual EVA frequency by country
# --------------------------------------------------

evas_per_year <- df |>
  filter(country %in% c("USA", "Russia")) |>
  filter(!is.na(year)) |>
  count(year, country)

p1 <- ggplot(evas_per_year, aes(x = year, y = n, fill = country)) +
  geom_col(position = "stack", alpha = 0.85) +
  scale_fill_manual(values = colour_map) +
  theme_minimal(base_size = 10)

ggsave("results/figures/fig_evas_per_year.png", plot = p1,
       width = 8, height = 4, dpi = 150)

# --------------------------------------------------
# Figure 2: Cumulative EVA count by country
# --------------------------------------------------

cum_data <- df |>
  filter(country %in% c("USA", "Russia")) |>
  filter(!is.na(date)) |>
  arrange(date) |>
  group_by(country) |>
  mutate(cum_evas = row_number()) |>
  ungroup()

p2 <- ggplot(cum_data, aes(x = date, y = cum_evas, colour = country)) +
  geom_line(linewidth = 1) +
  scale_colour_manual(values = colour_map) +
  theme_minimal(base_size = 10)

ggsave("results/figures/fig_cumulative_count.png", plot = p2,
       width = 8, height = 4, dpi = 150)

# --------------------------------------------------
# Figure 3: EVA duration over time (scatter + smoother)
# --------------------------------------------------

df_scatter <- df |>
  filter(!is.na(date), !is.na(duration), duration != "") |>
  rowwise() |>
  mutate(dur_parts = list(strsplit(duration, ":")[[1]]),
         duration_hrs = as.numeric(dur_parts[1]) + as.numeric(dur_parts[2]) / 60) |>
  ungroup() |>
  filter(!is.na(duration_hrs), country %in% c("USA", "Russia"))

p3 <- ggplot(df_scatter, aes(x = date, y = duration_hrs, colour = country)) +
  geom_point(alpha = 0.4, size = 1.2) +
  geom_smooth(method = "loess", se = FALSE, linewidth = 1) +
  scale_colour_manual(values = colour_map) +
  theme_minimal(base_size = 10)

ggsave("results/figures/fig_duration_over_time.png", plot = p3,
       width = 8, height = 4, dpi = 150)

print("R figures generated.")
