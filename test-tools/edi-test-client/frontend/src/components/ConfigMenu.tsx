import { useState } from "react";
import { useApiCall } from "../hooks/useApiCall";

export const ConfigMenu = () => {
  const { apiCall } = useApiCall();
  const [rpsInput, setRpsInput] = useState<string>("");
  const [transactionInput, setTransactionInput] = useState("");

  return (
    <div>
      <h2>Configuration</h2>
      <div>
        <label>RPS:</label>
        <input
          type="number"
          step="0.1"
          value={rpsInput}
          onChange={(e) => setRpsInput(e.target.value)}
        />
        <button
          onClick={() => apiCall("rps", "POST", { rps: parseFloat(rpsInput) })}
        >
          Update
        </button>
      </div>
      <div>
        <label>Transaction:</label>
        <select
          value={transactionInput}
          onChange={(e) => setTransactionInput(e.target.value)}
        >
          <option value="270">270</option>
          <option value="276">276</option>
          <option value="278">278</option>
        </select>
        <button
          onClick={() =>
            apiCall("transaction", "POST", {
              transaction: parseInt(transactionInput),
            })
          }
        >
          Update
        </button>
      </div>
    </div>
  );
};
