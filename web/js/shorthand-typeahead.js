// Set up Typeahead
var searchNotes = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/api/v1/typeahead?query=%QUERY',
    wildcard: '%QUERY'
  }
});

$('.typeahead').typeahead(null, {
  name: 'search-notes',
  source: searchNotes
});
