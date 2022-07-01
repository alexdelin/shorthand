import { useState, Suspense } from 'react';
import { SuspenseFallback } from '../components/SuspenseFallback';
import { FileSearchResults } from '../components/FileSearchResults';
import { FullTextSearchResults } from '../components/FullTextSearchResults';
import { SearchPageWrapper, SearchBar, SearchBarWrapper } from './SearchPage.styles'


export function SearchPage() {

  const [search, setSearch] = useState('');

  function handleSearchChange(event: React.ChangeEvent<HTMLInputElement>) {
    setTimeout(() => {
        setSearch(event.target.value)
      },
      500
    );
  }

  return (
    <SearchPageWrapper>
      <h2>Search</h2>
      <SearchBarWrapper>
        <SearchBar
          type="text"
          name="search"
          onChange={handleSearchChange}
          label="Search"
          variant="outlined"
        />
      </SearchBarWrapper>
      <Suspense fallback={SuspenseFallback}>
        <FileSearchResults query={search} />
      </Suspense>
      <Suspense fallback={SuspenseFallback}>
        <FullTextSearchResults query={search} />
      </Suspense>
    </SearchPageWrapper>
  )

}
