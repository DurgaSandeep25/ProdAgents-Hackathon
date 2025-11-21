const coins = [
  { symbol: 'BTC', name: 'Bitcoin' },
  { symbol: 'ETH', name: 'Ethereum' },
  { symbol: 'USDT', name: 'Tether' },
  { symbol: 'BNB', name: 'BNB' },
  { symbol: 'SOL', name: 'Solana' },
  { symbol: 'USDC', name: 'USD Coin' },
  { symbol: 'XRP', name: 'Ripple' },
  { symbol: 'DOGE', name: 'Dogecoin' },
  { symbol: 'ADA', name: 'Cardano' },
  { symbol: 'TRX', name: 'TRON' },
]

function CoinSelector({ selectedCoin, onCoinChange, disabled }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">
        Select Cryptocurrency
      </label>
      <select
        value={selectedCoin}
        onChange={(e) => onCoinChange(e.target.value)}
        disabled={disabled}
        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {coins.map((coin) => (
          <option key={coin.symbol} value={coin.symbol}>
            {coin.symbol} - {coin.name}
          </option>
        ))}
      </select>
    </div>
  )
}

export default CoinSelector

