import "./App.css";
import { StatusDisplay } from "./components/StatusDisplay";
import { ConfigMenu } from "./components/ConfigMenu";
import { StatsDisplay } from "./components/StatsDisplay";
import { ControlPanel } from "./components/ControlPanel";
import { StatusCodeChart } from "./components/StatusCodeChart";
import { useApiData } from "./hooks/useApiData";

function App() {
  const { status, stats } = useApiData();

  return (
    <div>
      <h1>EDI Test Client Dashboard</h1>
      <StatusDisplay status={status} />
      <ControlPanel status={status} />
      <ConfigMenu />
      <StatusCodeChart stats={stats} />
      <StatsDisplay stats={stats} />
    </div>
  );
}

export default App;
