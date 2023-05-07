NEW IDEA:

STAT SCRAPER:

    Purpose:
            Right now data interpretation is pretty scattered. Many classes need the same information
        and I implement different ways to access it in each place. This would centralize the storage
        of information. Instead of making calculations for themselves, other classes store a
        copy of the stat scraper. Then, the stat scraper can maximize speed and storage for each query.

        Other classes will simply ask stat scraper to make most calculations for them

    Representation:
        list or dataframe games
        store frequently needed values/ expensive things to calculate

        or 

        No storage, just calculations: lets classes decide which games to include

    Functions:
        efficiently perfrom queries/lookups/calculations on data


