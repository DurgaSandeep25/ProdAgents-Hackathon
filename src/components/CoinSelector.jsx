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
  const selectedCoinData = coins.find(c => c.symbol === selectedCoin)
  
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
        <span className="text-lg">📊</span>
        Select Asset to Analyze
      </label>
      <div className="relative">
        <select
          value={selectedCoin}
          onChange={(e) => onCoinChange(e.target.value)}
          disabled={disabled}
          className="w-full px-4 py-4 bg-gray-700/50 border-2 border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all appearance-none cursor-pointer hover:border-gray-500"
        >
          {coins.map((coin) => (
            <option key={coin.symbol} value={coin.symbol}>
              {coin.symbol} - {coin.name}
            </option>
          ))}
        </select>
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      {selectedCoinData && (
        <div className="mt-3 px-3 py-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg">
          <div className="text-xs text-gray-400">Selected</div>
          <div className="text-sm font-semibold text-blue-300">{selectedCoinData.symbol} - {selectedCoinData.name}</div>
        </div>
      )}
    </div>
  )
}

export default CoinSelector

