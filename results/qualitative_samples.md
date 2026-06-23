| Code (truncated) | Predicted | Reference |
|---|---|---|
| `protected int[] getFringeIndexes (int bits)     {         int index = BITS_TO_INDEX[bits];         if (index != -1) {             int[] ret = new int[` | /*
(non-Javadoc)

@see #getFringeIndexes(int) | Get the fringe index specified by the fringebits. If no index is available, try breaking
down the bits into contiguous regions of bits and look for indexes for those. |
| `def _download_metadata_archive(self):                  with tempfile.NamedTemporaryFile(delete=False) as metadata_archive:             shutil.copyfile` | Download the metadata archive from the catalog source.

        :return: | Makes a remote call to the Project Gutenberg servers and downloads
        the entire Project Gutenberg meta-data catalog. The catalog describes
        the texts on Project Gutenberg in RDF. The function returns a
        file-pointer to the catalog. |
| `@SuppressWarnings("rawtypes")     private Map<EntitySpec, SQLGenResultProcessorFactory> allEntitySpecToResultProcessor() {         /*          * The o` | Returns the result processor for all entity specs.

@return the result processor for all entity specs. | /*
We need to store multiple types of result processor factories in the same
map |
| `public function getCacheData($pCoord) { 		//	Check if the entry that has been requested actually exists 		if (!isset($this->_cellCache[$pCoord])) {` | Get the cache data for the given coordinate.

@param		int | Get cell at a specific coordinate

@param 	string 			$pCoord		Coordinate of the cell
@throws 	PHPExcel_Exception
@return 	PHPExcel_Cell 	Cell that was found, or null if not found |
| `def links       @_links \|\|= {}.tap do \|links\|         Array(headers["Link"] \|\| headers["link"]).map do \|link\|           link.match %r{\A<([^>]` | Returns a Hash of Hash of Link objects.

 @return Hash of Hash of Link objects. | See: http://tools.ietf.org/html/rfc5988 |
| `protected function convertBooleanStrings($v)     {         if (is_array($v)) {             return array_map(array( $this, 'convertBooleanStrings' ), $` | convertBooleanStrings

@param mixed $v

@return mixed | Converts 'true' and 'false' strings to TRUE and FALSE

@param $v

@return bool\|array |
| `public void unproject(double x, double y, double z, double[] out) {     glu.gluUnProject(x, y, z, modelview, 0, projection, 0, viewp, 0, out, 0);   }` | Unproject a vector.

@param x
@param y
@param z
@param out
@return | Unproject a screen coordinate (at depth 0) to 3D model coordinates.

@param x X
@param y Y
@param z Z
@param out output buffer |
| `func NewClient(baseAddr string) *Client { 	return &Client{ 		baseAddr: baseAddr, 		client:   &http.Client{}, 	} }` | // NewClient creates a new Client | // NewClient creates a new statusio client for the *public api*.
// baseAddr is i.e. status.example.copm/api/v2/ |
| `protected void writeListNumbers(final OutputStream result) throws IOException {          if(listLevel > 0) {             result.write(RtfList.LIST_` | Writes the list numbers to the given output stream.

@param result the output stream.
@throws IOException | Writes only the list number and list level number.

@param result The <code>OutputStream</code> to write to
@throws IOException On i/o errors. |
| `@Override 	public void handleRequest(final Request request) { 		super.handleRequest(request);  		WComponent visibleDialog = getVisible();  		if (visib` | Handle the request.

@param request
the request to handle
@return | Since none of the children are visible to standard processing, handleRequest has been overridden so that the
visible card is processed.

@param request the request being responded to. |