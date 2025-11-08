// Investment Portfolio Manager
// Manages B3 portfolio data with allocation recommendations

class PortfolioManager {
    constructor() {
        this.portfolio = {
            assetClasses: {},
            totalValue: 0,
            lastUpdate: null
        };
        this.targetAllocations = {};
        this.yahooFinanceCache = {};
        this.loadFromStorage();
    }

    // Parse B3 Excel file
    async parseExcelFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    
                    this.portfolio = {
                        assetClasses: {},
                        totalValue: 0,
                        lastUpdate: new Date().toISOString()
                    };

                    // Process each sheet
                    workbook.SheetNames.forEach(sheetName => {
                        const worksheet = workbook.Sheets[sheetName];
                        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
                        this.processSheet(sheetName, jsonData);
                    });

                    this.calculateTotalValue();
                    this.saveToStorage();
                    resolve(this.portfolio);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    processSheet(sheetName, data) {
        if (data.length < 2) return; // Need at least header and one row

        const headers = data[0];
        const rows = data.slice(1);

        // Identify key columns based on B3 format
        // For Renda Fixa, "Código" is the identifier (not a ticker but unique code)
        const tickerCol = this.findColumn(headers, ['Código de Negociação', 'Código', 'Ticker', 'Ativo']);
        const nameCol = this.findColumn(headers, ['Produto', 'Nome', 'Descrição', 'Razão Social']);
        const emissorCol = this.findColumn(headers, ['Emissor']); // For Renda Fixa
        const quantityCol = this.findColumn(headers, ['Quantidade', 'Qtd', 'Saldo']);
        // For Renda Fixa, use "Preço Atualizado CURVA" or similar
        const priceCol = this.findColumn(headers, ['Preço de Fechamento', 'Preço Atualizado CURVA', 'Preço Atualizado MTM', 'Preço Atualizado', 'Preço', 'Cotação', 'Preço Unitário', 'Valor Unitário']);
        // For Renda Fixa, use "Valor Atualizado CURVA" or similar
        const valueCol = this.findColumn(headers, ['Valor Atualizado', 'Valor Atualizado CURVA', 'Valor Atualizado MTM', 'Valor Atualizado FECHAMENTO', 'Valor', 'Total', 'Valor Total', 'Saldo em Reais']);

        if (!this.portfolio.assetClasses[sheetName]) {
            this.portfolio.assetClasses[sheetName] = {
                name: this.normalizeClassName(sheetName),
                assets: [],
                totalValue: 0
            };
        }

        rows.forEach(row => {
            if (!row || row.length === 0) return;

            const ticker = tickerCol >= 0 ? this.cleanString(row[tickerCol]) : null;
            const name = nameCol >= 0 ? this.cleanString(row[nameCol]) : null;
            const emissor = emissorCol >= 0 ? this.cleanString(row[emissorCol]) : null;
            const quantity = quantityCol >= 0 ? this.parseNumber(row[quantityCol]) : 0;
            const price = priceCol >= 0 ? this.parseNumber(row[priceCol]) : 0;
            let value = valueCol >= 0 ? this.parseNumber(row[valueCol]) : 0;

            // Calculate value if not provided
            if (!value && quantity && price) {
                value = quantity * price;
            }

            // Only add if we have meaningful data
            if ((ticker || name) && value > 0) {
                const asset = {
                    ticker: ticker || emissor || 'N/A',
                    name: name || ticker || emissor || 'Sem nome',
                    quantity: quantity,
                    price: price,
                    value: value,
                    class: sheetName,
                    emissor: emissor || null,
                    yahooData: null
                };

                this.portfolio.assetClasses[sheetName].assets.push(asset);
                this.portfolio.assetClasses[sheetName].totalValue += value;
            }
        });
    }

    findColumn(headers, possibleNames) {
        for (let name of possibleNames) {
            const index = headers.findIndex(h => 
                h && h.toString().toLowerCase().includes(name.toLowerCase())
            );
            if (index >= 0) return index;
        }
        return -1;
    }

    cleanString(value) {
        if (!value) return null;
        return value.toString().trim();
    }

    parseNumber(value) {
        if (typeof value === 'number') return value;
        if (!value) return 0;
        
        const str = value.toString()
            .replace(/[^\d,.-]/g, '')
            .replace('.', '')
            .replace(',', '.');
        
        const num = parseFloat(str);
        return isNaN(num) ? 0 : num;
    }

    normalizeClassName(name) {
        const nameMap = {
            'Ações': 'Ações',
            'Acoes': 'Ações',
            'FII': 'Fundos Imobiliários',
            'Fundo de Investimento': 'Fundos Imobiliários',
            'Fundos Imobiliários': 'Fundos Imobiliários',
            'Renda Fixa': 'Renda Fixa',
            'Tesouro Direto': 'Tesouro Direto',
            'BDR': 'BDRs',
            'ETF': 'ETFs',
            'Stocks': 'Ações Internacionais'
        };

        for (let [key, value] of Object.entries(nameMap)) {
            if (name.toLowerCase().includes(key.toLowerCase())) {
                return value;
            }
        }
        return name;
    }

    calculateTotalValue() {
        this.portfolio.totalValue = Object.values(this.portfolio.assetClasses)
            .reduce((sum, assetClass) => sum + assetClass.totalValue, 0);
    }

    // Yahoo Finance integration
    async fetchYahooFinanceData(ticker, assetClass) {
        // Check cache first
        if (this.yahooFinanceCache[ticker]) {
            return this.yahooFinanceCache[ticker];
        }

        // Only fetch for relevant asset classes (skip Renda Fixa, Tesouro Direto as they don't have tickers)
        const relevantClasses = ['Ações', 'FII', 'Fundos Imobiliários', 'BDRs', 'ETFs', 'Ações Internacionais'];
        const normalizedClass = this.normalizeClassName(assetClass);
        
        if (!relevantClasses.includes(normalizedClass)) {
            return null;
        }

        try {
            // Format ticker for Yahoo Finance (B3 stocks need .SA suffix)
            let yahooTicker = ticker;
            if (normalizedClass === 'Ações' || normalizedClass === 'Fundos Imobiliários') {
                yahooTicker = `${ticker}.SA`;
            }

            // Use Yahoo Finance API (via yfinance-proxy or similar service)
            // For demonstration, we'll use a mock structure
            // In production, you'd call: https://query1.finance.yahoo.com/v8/finance/chart/${yahooTicker}
            
            const data = {
                ticker: yahooTicker,
                currentPrice: null,
                change: null,
                changePercent: null,
                volume: null,
                marketCap: null,
                pe: null,
                dividendYield: null,
                lastUpdate: new Date().toISOString()
            };

            this.yahooFinanceCache[ticker] = data;
            return data;
        } catch (error) {
            console.warn(`Could not fetch data for ${ticker}:`, error);
            return null;
        }
    }

    async enrichPortfolioWithYahooData() {
        const promises = [];
        
        for (let className in this.portfolio.assetClasses) {
            const assetClass = this.portfolio.assetClasses[className];
            
            for (let asset of assetClass.assets) {
                if (asset.ticker && asset.ticker !== 'N/A') {
                    promises.push(
                        this.fetchYahooFinanceData(asset.ticker, className)
                            .then(data => {
                                asset.yahooData = data;
                            })
                    );
                }
            }
        }

        await Promise.all(promises);
        this.saveToStorage();
    }

    // Allocation management
    setTargetAllocation(className, percentage) {
        this.targetAllocations[className] = Math.max(0, Math.min(100, percentage));
        this.saveToStorage();
    }

    getTargetAllocation(className) {
        return this.targetAllocations[className] || 0;
    }

    getTotalTargetAllocation() {
        return Object.values(this.targetAllocations).reduce((sum, val) => sum + val, 0);
    }

    // Calculate rebalancing recommendations
    calculateRecommendations() {
        const recommendations = [];
        const totalValue = this.portfolio.totalValue;

        if (totalValue === 0) return recommendations;

        for (let className in this.portfolio.assetClasses) {
            const assetClass = this.portfolio.assetClasses[className];
            const currentValue = assetClass.totalValue;
            const currentPercentage = (currentValue / totalValue) * 100;
            const targetPercentage = this.getTargetAllocation(className);

            if (targetPercentage > 0) {
                const targetValue = (targetPercentage / 100) * totalValue;
                const difference = targetValue - currentValue;
                const differencePercentage = targetPercentage - currentPercentage;

                recommendations.push({
                    className: assetClass.name,
                    currentValue,
                    currentPercentage,
                    targetPercentage,
                    targetValue,
                    difference,
                    differencePercentage,
                    action: difference > 0 ? 'COMPRAR' : difference < 0 ? 'VENDER' : 'OK'
                });
            }
        }

        return recommendations.sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference));
    }

    // Storage management
    saveToStorage() {
        try {
            localStorage.setItem('portfolio', JSON.stringify(this.portfolio));
            localStorage.setItem('targetAllocations', JSON.stringify(this.targetAllocations));
            localStorage.setItem('yahooFinanceCache', JSON.stringify(this.yahooFinanceCache));
        } catch (error) {
            console.error('Error saving to storage:', error);
        }
    }

    loadFromStorage() {
        try {
            const portfolioData = localStorage.getItem('portfolio');
            const allocationsData = localStorage.getItem('targetAllocations');
            const cacheData = localStorage.getItem('yahooFinanceCache');

            if (portfolioData) {
                this.portfolio = JSON.parse(portfolioData);
            }
            if (allocationsData) {
                this.targetAllocations = JSON.parse(allocationsData);
            }
            if (cacheData) {
                this.yahooFinanceCache = JSON.parse(cacheData);
            }
        } catch (error) {
            console.error('Error loading from storage:', error);
        }
    }

    clearStorage() {
        localStorage.removeItem('portfolio');
        localStorage.removeItem('targetAllocations');
        localStorage.removeItem('yahooFinanceCache');
    }

    hasData() {
        return Object.keys(this.portfolio.assetClasses).length > 0;
    }
}

// UI Manager
class UIManager {
    constructor(portfolioManager) {
        this.pm = portfolioManager;
        this.initializeEventListeners();
        this.loadExistingData();
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) this.handleFileUpload(file);
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) this.handleFileUpload(file);
        });

        document.getElementById('saveAllocationBtn').addEventListener('click', () => {
            this.saveAllocations();
        });
    }

    async handleFileUpload(file) {
        if (!file.name.match(/\.(xlsx|xls)$/)) {
            alert('Por favor, selecione um arquivo Excel válido (.xlsx ou .xls)');
            return;
        }

        this.showLoading(true);

        try {
            await this.pm.parseExcelFile(file);
            await this.pm.enrichPortfolioWithYahooData();
            this.renderAll();
            this.showLoading(false);
        } catch (error) {
            console.error('Error processing file:', error);
            alert('Erro ao processar arquivo. Verifique o formato e tente novamente.');
            this.showLoading(false);
        }
    }

    loadExistingData() {
        if (this.pm.hasData()) {
            this.renderAll();
        }
    }

    renderAll() {
        this.renderSummary();
        this.renderAllocationInputs();
        this.renderRecommendations();
        this.renderAssetClasses();
    }

    renderSummary() {
        const summarySection = document.getElementById('summarySection');
        summarySection.classList.remove('hidden');

        const totalValue = this.pm.portfolio.totalValue;
        const assetClassCount = Object.keys(this.pm.portfolio.assetClasses).length;
        const totalAssets = Object.values(this.pm.portfolio.assetClasses)
            .reduce((sum, ac) => sum + ac.assets.length, 0);

        document.getElementById('totalValue').textContent = this.formatCurrency(totalValue);
        document.getElementById('assetClasses').textContent = assetClassCount;
        document.getElementById('totalAssets').textContent = totalAssets;
        
        if (this.pm.portfolio.lastUpdate) {
            const date = new Date(this.pm.portfolio.lastUpdate);
            document.getElementById('lastUpdate').textContent = date.toLocaleString('pt-BR');
        }
    }

    renderAllocationInputs() {
        const allocationSection = document.getElementById('allocationSection');
        const inputsContainer = document.getElementById('allocationInputs');
        
        allocationSection.classList.remove('hidden');
        inputsContainer.innerHTML = '';

        for (let className in this.pm.portfolio.assetClasses) {
            const assetClass = this.pm.portfolio.assetClasses[className];
            const currentPercentage = ((assetClass.totalValue / this.pm.portfolio.totalValue) * 100).toFixed(2);
            const targetPercentage = this.pm.getTargetAllocation(className);

            const div = document.createElement('div');
            div.className = 'bg-gray-50 p-4 rounded-lg';
            div.innerHTML = `
                <label class="block text-sm font-semibold text-gray-700 mb-2">
                    ${assetClass.name}
                    <span class="text-xs font-normal text-gray-500">(Atual: ${currentPercentage}%)</span>
                </label>
                <div class="flex items-center space-x-2">
                    <input 
                        type="number" 
                        min="0" 
                        max="100" 
                        step="0.1"
                        value="${targetPercentage}"
                        data-class="${className}"
                        class="allocation-input flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                    <span class="text-gray-600 font-semibold">%</span>
                </div>
            `;
            inputsContainer.appendChild(div);
        }

        // Add event listeners
        document.querySelectorAll('.allocation-input').forEach(input => {
            input.addEventListener('input', () => this.updateTotalAllocation());
        });

        this.updateTotalAllocation();
    }

    updateTotalAllocation() {
        const inputs = document.querySelectorAll('.allocation-input');
        let total = 0;
        inputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });

        const totalElement = document.getElementById('totalAllocation');
        totalElement.textContent = total.toFixed(2) + '%';
        
        if (Math.abs(total - 100) < 0.01) {
            totalElement.classList.remove('text-red-600');
            totalElement.classList.add('text-green-600');
        } else {
            totalElement.classList.remove('text-green-600');
            totalElement.classList.add('text-red-600');
        }
    }

    saveAllocations() {
        const inputs = document.querySelectorAll('.allocation-input');
        inputs.forEach(input => {
            const className = input.dataset.class;
            const percentage = parseFloat(input.value) || 0;
            this.pm.setTargetAllocation(className, percentage);
        });

        this.renderRecommendations();
        
        // Show feedback
        const btn = document.getElementById('saveAllocationBtn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Salvo!';
        btn.classList.add('bg-green-500');
        btn.classList.remove('bg-blue-500');
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('bg-green-500');
            btn.classList.add('bg-blue-500');
        }, 2000);
    }

    renderRecommendations() {
        const recommendationsSection = document.getElementById('recommendationsSection');
        const recommendationsContent = document.getElementById('recommendationsContent');

        const recommendations = this.pm.calculateRecommendations();

        if (recommendations.length === 0) {
            recommendationsSection.classList.add('hidden');
            return;
        }

        recommendationsSection.classList.remove('hidden');
        recommendationsContent.innerHTML = '';

        recommendations.forEach(rec => {
            const div = document.createElement('div');
            div.className = 'border-l-4 p-4 mb-4 rounded-r-lg ' + 
                (rec.action === 'COMPRAR' ? 'border-green-500 bg-green-50' : 
                 rec.action === 'VENDER' ? 'border-red-500 bg-red-50' : 
                 'border-gray-400 bg-gray-50');

            div.innerHTML = `
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h3 class="font-bold text-lg text-gray-800">${rec.className}</h3>
                        <div class="grid grid-cols-2 gap-4 mt-2 text-sm">
                            <div>
                                <p class="text-gray-600">Atual: ${this.formatCurrency(rec.currentValue)} (${rec.currentPercentage.toFixed(2)}%)</p>
                                <p class="text-gray-600">Meta: ${this.formatCurrency(rec.targetValue)} (${rec.targetPercentage.toFixed(2)}%)</p>
                            </div>
                            <div>
                                <p class="text-gray-600">Diferença: ${this.formatCurrency(Math.abs(rec.difference))}</p>
                                <p class="text-gray-600">Variação: ${rec.differencePercentage.toFixed(2)} pontos percentuais</p>
                            </div>
                        </div>
                    </div>
                    <div class="ml-4">
                        <span class="inline-block px-4 py-2 rounded-lg font-bold text-white ${
                            rec.action === 'COMPRAR' ? 'bg-green-500' :
                            rec.action === 'VENDER' ? 'bg-red-500' :
                            'bg-gray-500'
                        }">
                            ${rec.action}
                        </span>
                    </div>
                </div>
            `;
            recommendationsContent.appendChild(div);
        });
    }

    renderAssetClasses() {
        const detailsSection = document.getElementById('detailsSection');
        const container = document.getElementById('assetClassesContainer');
        
        detailsSection.classList.remove('hidden');
        container.innerHTML = '';

        for (let className in this.pm.portfolio.assetClasses) {
            const assetClass = this.pm.portfolio.assetClasses[className];
            const percentage = ((assetClass.totalValue / this.pm.portfolio.totalValue) * 100).toFixed(2);

            const div = document.createElement('div');
            div.className = 'bg-white rounded-lg shadow-md p-6 mb-6';
            
            let assetsHTML = '';
            assetClass.assets.forEach(asset => {
                const assetPercentage = ((asset.value / assetClass.totalValue) * 100).toFixed(2);
                assetsHTML += `
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 border-b">
                            <div>
                                <p class="font-semibold text-gray-800">${asset.ticker}</p>
                                <p class="text-xs text-gray-500">${asset.name}</p>
                            </div>
                        </td>
                        <td class="px-4 py-3 border-b text-right">${this.formatNumber(asset.quantity)}</td>
                        <td class="px-4 py-3 border-b text-right">${this.formatCurrency(asset.price)}</td>
                        <td class="px-4 py-3 border-b text-right font-semibold">${this.formatCurrency(asset.value)}</td>
                        <td class="px-4 py-3 border-b text-right text-sm text-gray-600">${assetPercentage}%</td>
                    </tr>
                `;
            });

            div.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold text-gray-800">${assetClass.name}</h3>
                    <div class="text-right">
                        <p class="text-2xl font-bold text-blue-600">${this.formatCurrency(assetClass.totalValue)}</p>
                        <p class="text-sm text-gray-600">${percentage}% do total</p>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr class="bg-gray-100">
                                <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700">Ativo</th>
                                <th class="px-4 py-2 text-right text-sm font-semibold text-gray-700">Quantidade</th>
                                <th class="px-4 py-2 text-right text-sm font-semibold text-gray-700">Preço</th>
                                <th class="px-4 py-2 text-right text-sm font-semibold text-gray-700">Valor</th>
                                <th class="px-4 py-2 text-right text-sm font-semibold text-gray-700">%</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${assetsHTML}
                        </tbody>
                    </table>
                </div>
            `;
            container.appendChild(div);
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    formatNumber(value) {
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(value);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    const portfolioManager = new PortfolioManager();
    const uiManager = new UIManager(portfolioManager);
});
