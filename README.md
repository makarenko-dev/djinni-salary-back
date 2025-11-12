# Djinni salary backend

This project is the backend for the Chrome extension, which can be found [here](https://github.com/makarenko-dev/djinni-salary-plugin)

It helps determine the hidden salary values for vacancies on [Djinni](https://djinni.co)

## How It Works

When a request is received from the client, the system checks whether the salary for the requested vacancy already exists in the database.
If not, it scrapes the salary information from the website, saves it to the database, and uses it for faster responses in the future.

### How salary is scraped

Djinni allows filtering vacancies by salary (e.g., starting from $X) on a company’s page.
Although the salary is not displayed directly, it is reflected in the filtering logic.
By continuously adjusting the filter and finding the point where the target vacancy disappears, we can estimate the salary that was set.

A binary search algorithm is used to optimize this process.

During the binary search, the system also discovers partial salary boundaries (at least starting points) for many other vacancies.
These results are saved to the database as well, allowing future requests to start from a closer known range and reduce the number of scraping operations required.