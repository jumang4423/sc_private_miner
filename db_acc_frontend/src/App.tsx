import { useEffect, useState } from "react";
import axios from "axios";
import Accordion from "@mui/material/Accordion";
import AccordionActions from "@mui/material/AccordionActions";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import CircularProgress from "@mui/material/CircularProgress";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { Box } from "@mui/material";
import "./App.css";

const API_URL = "-";
const PAGE_SIZE = 15;
const columns: GridColDef[] = [
  {
    field: "id",
    headerName: "URL",
    width: 250,
    renderCell: (params) => (
      <a href={params.value} target="_blank" rel="noreferrer">
        {params.value}
      </a>
    ),
  },
  { field: "follower_count", headerName: "Followers", width: 100 },
  { field: "artist_name", headerName: "Artist Name", width: 150 },
  { field: "title", headerName: "Title", width: 150 },
  { field: "timestamp", headerName: "Timestamp", width: 200 },
];

const DataAnalyzer = () => {
  const [data, setData] = useState({
    urls: [],
    cursor: null,
    page: 1,
  });
  const [is_small, setIsSmall] = useState(0);
  const [desc_key, setDescKey] = useState("follower_count");
  const [is_loading, setIsLoading] = useState(false);

  const getUrls = async (is_init: boolean) => {
    setIsLoading(true);
    const doc = is_init ? null : data.cursor;
    const page = is_init ? 1 : data.page + 1;
    const res = await axios.get(
      `${API_URL}/urls?is_small=${is_small}&desc_key=${desc_key}&page_size=${PAGE_SIZE}${
        doc ? `&cursor=${doc}` : ""
      }`
    );
    const urls = res.data.urls.map((url: any) => {
      return {
        id: url.url,
        title: url.title,
        artist_name: url.artist_name,
        follower_count: url.follower_count,
        sender_name: url.sender_name,
        timestamp: url.timestamp,
      };
    });
    setData(
      structuredClone({ urls: urls, cursor: res.data.next_cursor, page })
    );
    setIsLoading(false);
  };
  useEffect(() => {
    getUrls(true);
  }, [is_small, desc_key]);

  return (
    <div>
      <AccordionDetails>
        <Box>
          <DataGrid
            rows={data.urls}
            columns={columns}
            pageSizeOptions={[PAGE_SIZE]}
            loading={is_loading}
          />
        </Box>
      </AccordionDetails>
      <AccordionActions>
        <button
          onClick={() => {
            setIsSmall((is_small) => (is_small ? 0 : 1));
          }}
        >
          {is_small ? "small artist" : "big artist"}
        </button>
        <button
          onClick={() => {
            setDescKey((desc_key) =>
              desc_key === "timestamp" ? "follower_count" : "timestamp"
            );
          }}
        >
          {desc_key === "timestamp" ? "sort by timestamp" : "sort by follower"}
        </button>
        <button
          style={{ backgroundColor: "lightgreen", color: "white" }}
          onClick={() => getUrls(false)}
        >
          go to page {data.page + 1}
        </button>
      </AccordionActions>
    </div>
  );
};

const URLGenerator = () => {
  const [rnd_url, setRndUrl] = useState("");
  const [is_loading, setIsLoading] = useState(false);
  const genRndUrl = async (is_small: number) => {
    setIsLoading(true);
    const res = await axios.get(
      `${API_URL}/random_private_url?is_small=${is_small}`
    );
    setRndUrl(res.data.url);
    setIsLoading(false);
  };
  return (
    <div>
      <AccordionDetails>
        {!is_loading &&
          (rnd_url !== "" ? (
            <a href={rnd_url} target="_blank" rel="noreferrer">
              {rnd_url}
            </a>
          ) : (
            <div>click the button to generate a random private url</div>
          ))}
        {is_loading && <CircularProgress />}
      </AccordionDetails>
      <AccordionActions>
        <button onClick={() => genRndUrl(0)}>gen big artist link</button>
        <button onClick={() => genRndUrl(1)}>gen small artist link</button>
      </AccordionActions>
    </div>
  );
};

function App() {
  const [is_data_analyzer_open, setIsDataAnalyzerOpen] = useState(false);
  const [is_url_generator_open, setIsUrlGeneratorOpen] = useState(false);

  return (
    <>
      <div className="App" style={{}}>
        <div
          style={{
            fontSize: "2rem",
            marginBottom: "8px",
          }}
        >
          (^^♪ sc-private-miner
        </div>
        <div style={{ fontSize: "1rem", marginBottom: "24px" }}>
          * dont comment to private tracks
          <br />* start mining from{" "}
          <a
            href="https://github.com/jumang4423/sc_private_miner"
            target="_blank"
            rel="noreferrer"
          >
            this repo
          </a>
        </div>
        <Accordion
          onChange={() => setIsDataAnalyzerOpen(!is_data_analyzer_open)}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <h2>📊 data analyzer </h2>
          </AccordionSummary>
          {is_data_analyzer_open && <DataAnalyzer />}
        </Accordion>
        <Accordion
          onChange={() => setIsUrlGeneratorOpen(!is_url_generator_open)}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <h2>🌈 random private url generator (dead, fixing rn)</h2>
          </AccordionSummary>
          {is_url_generator_open && <URLGenerator />}
        </Accordion>
      </div>
    </>
  );
}

export default App;
