import axios from 'axios';
import type { 
  FinancialSummary, 
  SalaryConfig, 
  Transaction, 
  FinancialAdvice, 
  LiquidityPrediction 
} from '../types';

/**
 * FINANCIAL SERVICE - API BRIDGE LAYER
 * 
 * Conexión real con API Gateway de AWS.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://p70gn8n0wg.execute-api.us-east-1.amazonaws.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// ID de usuario real de la siembra (Desarrollador Freelance)
const TEST_USER_ID = 'USR-FD8F0536';

export const financialService = {
  /**
   * Obtiene el resumen consolidado llamando al motor de smoothing.
   */
  getSummary: async (): Promise<FinancialSummary> => {
    try {
      const resp = await api.get(`/smoothing?user_id=${TEST_USER_ID}`);
      const data = resp.data;

      return {
        nextIncome: {
          amount: data.artificial_salary,
          date: new Date().toISOString().split('T')[0], // Hoy
          description: 'Depósito Incomia Garantizado'
        },
        stabilityReserve: {
          current: data.stabilization_fund,
          target: data.artificial_salary * 1.5, // Arbitrario para demo
          progress: data.resilience_indicator * 100,
          message: data.resilience_indicator > 0.5 ? 'Fondo sólido' : 'Construyendo reserva'
        },
        recentTransactions: [] // Se podría poblar con /income
      };
    } catch (error) {
      console.error('Error fetching summary:', error);
      throw error;
    }
  },

  getSalaryConfig: async (): Promise<SalaryConfig> => {
    try {
      const resp = await api.get(`/smoothing?user_id=${TEST_USER_ID}`);
      const data = resp.data;

      return {
        desiredAmount: data.artificial_salary,
        frequency: 'biweekly',
        recommendedAmount: data.artificial_salary * 1.1,
        impact: 15.5,
        confidence: 92
      };
    } catch (error) {
      console.error('Error fetching salary config:', error);
      throw error;
    }
  },

  updateSalaryConfig: async (config: Partial<SalaryConfig>): Promise<SalaryConfig> => {
    // Simulado para demo: En producción llamaría a un endpoint de settings
    return {
      desiredAmount: config.desiredAmount || 0,
      frequency: config.frequency || 'biweekly',
      recommendedAmount: (config.desiredAmount || 0) * 1.1,
      impact: 15.5,
      confidence: 92
    };
  },

  getTransactions: async (): Promise<Transaction[]> => {
    try {
      const resp = await api.get(`/income?account_id=64cfbe9096831d0339d67962`);
      // Mapear transacciones de Nessie a formato Incomia
      return (resp.data.incomes || []).map((inc: any, idx: number) => ({
        id: `txn-${idx}`,
        date: inc.date || new Date().toISOString(),
        source: 'Capital One (Nessie)',
        category: 'Income',
        amount: inc.amount,
        status: 'processed',
        type: 'income'
      }));
    } catch (error) {
      console.error('Error fetching transactions:', error);
      return [];
    }
  },

  getFinancialAdvice: async (): Promise<FinancialAdvice[]> => {
    try {
      const resp = await api.get(`/advice?user_id=${TEST_USER_ID}`);
      return [{
        id: 'advice-1',
        title: 'Consejo de Nova Pro',
        content: resp.data.advice,
        type: 'saving',
        date: new Date().toLocaleDateString(),
        impact: 'Alto'
      }];
    } catch (error) {
      console.error('Error fetching advice:', error);
      return [];
    }
  },

  getPredictions: async (): Promise<LiquidityPrediction[]> => {
    try {
      const resp = await api.get(`/predictions?user_id=${TEST_USER_ID}`);
      const data = resp.data;
      
      // Adaptar el resultado del motor de predicción
      return [{
        date: 'Próximos 14 días',
        probability: data.prediction?.bankruptcy_probability * 100 || 5,
        expectedBalance: data.prediction?.final_projected_balance || 0,
        riskLevel: data.prediction?.new_risk_score > 70 ? 'high' : 'low'
      }];
    } catch (error) {
      console.error('Error fetching predictions:', error);
      return [];
    }
  },

  uploadData: async (file: File): Promise<{ success: boolean; dataPoints: number }> => {
    console.log('[AWS Integration] S3 Uploading simulation:', file.name);
    return { success: true, dataPoints: 1284 };
  },

  // --- GESTIÓN DE GASTOS (Simulado para Demo) ---
  getExpenses: async (): Promise<any[]> => {
    // En producción esto sería GET /expenses?user_id=...
    return [
      { id: 'exp-1', category: 'Vivienda', concept: 'Renta Mensual', amount: 1200, type: 'fixed', date: '2026-06-01' },
      { id: 'exp-2', category: 'Comida', concept: 'Despensa Semanal', amount: 150, type: 'variable', date: '2026-06-05' },
    ];
  },

  addExpense: async (expense: any): Promise<any> => {
    console.log('[API] Agregando gasto:', expense);
    return { ...expense, id: `exp-${Math.random().toString(36).substr(2, 9)}` };
  },

  deleteExpense: async (id: string): Promise<void> => {
    console.log('[API] Eliminando gasto:', id);
  },

  getCashFlowHistory: async (): Promise<any[]> => {
    // Simulado basándose en datos que alimentan las gráficas
    return [
      { id: 'cf-1', month: 'Enero', real: 4200, stabilized: 3800 },
      { id: 'cf-2', month: 'Febrero', real: 3100, stabilized: 3800 },
      { id: 'cf-3', month: 'Marzo', real: 5600, stabilized: 3800 },
    ];
  }
};
