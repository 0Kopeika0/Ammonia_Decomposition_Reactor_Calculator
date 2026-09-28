import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.integrate import quad
import math

class AmmoniaReactorCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор реактора разложения аммиака")
        self.root.geometry("1100x650")
        
        # Установка шрифта
        self.font_size = 12
        self.set_font_style()
        
        # Константы
        self.R = 8.31
        self.calculating = False
        
        self.create_widgets()
    
    def set_font_style(self):
        """Установка стиля шрифта"""
        self.style = ttk.Style()
        self.style.configure('.', font=('Arial', self.font_size))
        self.style.configure('Title.TLabel', font=('Arial', self.font_size, 'bold'))
        self.style.configure('Section.TLabelframe', font=('Arial', self.font_size, 'bold'))
        self.style.configure('Section.TLabelframe.Label', font=('Arial', self.font_size, 'bold'))
        
        # Настройка шрифта для matplotlib
        plt.rcParams.update({
            'font.size': self.font_size,
            'axes.titlesize': self.font_size,
            'axes.labelsize': self.font_size,
            'xtick.labelsize': self.font_size - 1,
            'ytick.labelsize': self.font_size - 1,
            'legend.fontsize': self.font_size - 1
        })
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя часть - входные параметры
        input_frame = ttk.LabelFrame(main_frame, text="Параметры процесса", style='Section.TLabelframe', padding="8")
        input_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.create_input_widgets(input_frame)
        
        # Средняя часть - разделенная на результаты и графики
        results_graphs_frame = ttk.Frame(main_frame)
        results_graphs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Левая часть - результаты
        results_frame = ttk.LabelFrame(results_graphs_frame, text="Результаты расчета", style='Section.TLabelframe', padding="8")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.create_results_widgets(results_frame)
        
        # Правая часть - графики
        graph_frame = ttk.LabelFrame(results_graphs_frame, text="Графики", style='Section.TLabelframe', padding="8")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_graphs_widgets(graph_frame)
        
        # Начальное сообщение
        self.show_initial_message()
    
    def create_input_widgets(self, parent):
        """Создание виджетов ввода параметров"""
        row = 0
        
        # Температура
        ttk.Label(parent, text="Температура, °C:", style='TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
        self.temp_var = tk.DoubleVar(value=577)
        ttk.Entry(parent, textvariable=self.temp_var, width=10, font=('Arial', self.font_size)).grid(row=row, column=1, pady=2, padx=5)
        ttk.Scale(parent, from_=500, to=800, variable=self.temp_var, 
                 orient=tk.HORIZONTAL, length=150).grid(row=row, column=2, columnspan=2, pady=2, sticky=tk.EW)
        
        row += 1
        
        # Давление
        ttk.Label(parent, text="Давление, атм:", style='TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
        self.pressure_var = tk.DoubleVar(value=1.0)
        ttk.Entry(parent, textvariable=self.pressure_var, width=10, font=('Arial', self.font_size)).grid(row=row, column=1, pady=2, padx=5)
        ttk.Scale(parent, from_=0.5, to=5.0, variable=self.pressure_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=row, column=2, columnspan=2, pady=2, sticky=tk.EW)
        
        row += 1
        
        # Расход смеси
        ttk.Label(parent, text="Расход смеси, м³/ч:", style='TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
        self.flow_var = tk.DoubleVar(value=21500)
        ttk.Entry(parent, textvariable=self.flow_var, width=10, font=('Arial', self.font_size)).grid(row=row, column=1, pady=2, padx=5)
        ttk.Scale(parent, from_=21000, to=25000, variable=self.flow_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=row, column=2, columnspan=2, pady=2, sticky=tk.EW)
        
        row += 1
        
        # Мольная доля NH3
        ttk.Label(parent, text="Мольная доля NH₃:", style='TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
        self.nh3_frac_var = tk.DoubleVar(value=0.18)
        ttk.Entry(parent, textvariable=self.nh3_frac_var, width=10, font=('Arial', self.font_size)).grid(row=row, column=1, pady=2, padx=5)
        ttk.Scale(parent, from_=0.18, to=0.22, variable=self.nh3_frac_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=row, column=2, columnspan=2, pady=2, sticky=tk.EW)
        
        row += 1
        
        # Целевая производительность
        ttk.Label(parent, text="Производительность H₂, м³/ч:", style='TLabel').grid(row=row, column=0, sticky=tk.W, pady=2)
        self.target_h2_var = tk.DoubleVar(value=4800)
        ttk.Entry(parent, textvariable=self.target_h2_var, width=10, font=('Arial', self.font_size)).grid(row=row, column=1, pady=2, padx=5)
        
        row += 1
        
        # Кнопки
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=4, pady=8)
        
        ttk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Тест", command=self.test_composition_dependence).pack(side=tk.LEFT, padx=5)
        
        # Настройка весов колонок для растягивания
        parent.columnconfigure(2, weight=1)
    
    def create_results_widgets(self, parent):
        """Создание виджетов для отображения результатов"""
        # Scrollbar для результатов
        scroll_frame = ttk.Frame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar = ttk.Scrollbar(scroll_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_text = tk.Text(scroll_frame, wrap=tk.NONE,
                                   xscrollcommand=x_scrollbar.set,
                                   yscrollcommand=y_scrollbar.set,
                                   font=('Courier', self.font_size), 
                                   bg='#f8f9fa',
                                   padx=10, pady=10)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.results_text.yview)
        x_scrollbar.config(command=self.results_text.xview)
    
    def create_graphs_widgets(self, parent):
        """Создание виджетов для графиков"""
        # Создаем фигуру с 3 подграфиками
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(8, 6))
        self.fig.tight_layout(pad=4.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def show_initial_message(self):
        """Показать начальное сообщение"""
        initial_text = """
Для начала расчета введите параметры 
и нажмите кнопку "Рассчитать"

Параметры по умолчанию:
• Температура: 577 °C
• Давление: 1.0 атм
• Расход: 21500 м³/ч  
• Доля NH₃: 0.18
• Целевой H₂: 4800 м³/ч
"""
        self.results_text.insert(1.0, initial_text)
    
    def k1(self, T):
        """Константа скорости прямой реакции"""
        return 18.56e9 * math.exp(-142630 / (self.R * T))
    
    def kp(self, T):
        """Константа равновесия"""
        return 10**(5 - 2000/T)
    
    def reaction_rate(self, X, T, P, NH3_0):
        """Скорость реакции разложения аммиака"""
        try:
            # Состав реакционной смеси
            NH3_remaining = NH3_0 * (1 - X)
            H2_produced = 0.01 + 1.5 * NH3_0 * X
            N2_produced = 0.01 + 0.5 * NH3_0 * X
            CH4_inert = 0.80 - NH3_0  # Метан как инертная составляющая
            
            # Суммарная мольная доля (должна быть равна 1)
            total_moles = NH3_remaining + H2_produced + N2_produced + CH4_inert
            
            # Парциальные давления
            P_NH3 = (NH3_remaining / total_moles) * P
            P_H2 = (H2_produced / total_moles) * P
            P_N2 = (N2_produced / total_moles) * P
            
            if P_NH3 <= 0 or P_H2 <= 0:
                return 1e-10
                
            term1 = (P_NH3 / (P_H2**1.5))**0.25
            term2 = (P_N2 * P_H2**1.5) / (P_NH3 * self.kp(T))
            
            rate = (self.k1(T) / P) * (term1 - term2)
            return max(rate, 1e-10)
            
        except:
            return 1e-10
    
    def calculate_reactor_volume(self, T, P, F, NH3_0, target_H2):
        """Расчет объема реактора идеального вытеснения"""
        T_kelvin = T + 273.15
        
        # РАСЧЕТ ТРЕБУЕМОЙ СТЕПЕНИ ПРЕВРАЩЕНИЯ
        try:
            # Общий мольный расход (идеальный газ)
            total_molar_flow = (F * 1000) / 22.4  # моль/ч
            
            # Мольный расход аммиака
            F_NH3 = total_molar_flow * NH3_0  # моль/ч
            
            # Теоретическое количество водорода из полного превращения аммиака
            theoretical_H2 = F_NH3 * 1.5 * 22.4 / 1000  # м³/ч
            
            # Требуемая степень превращения
            X_required = target_H2 / theoretical_H2 if theoretical_H2 > 0 else 0
            X_required = min(max(X_required, 0.01), 0.99)
            
        except Exception as e:
            return None, None, str(e)
        
        # РАСЧЕТ ИНТЕГРАЛА ДЛЯ ОБЪЕМА РИВ
        try:
            def integrand(X):
                rate = self.reaction_rate(X, T_kelvin, P, NH3_0)
                if rate <= 1e-10:
                    return 1e10
                return 1.0 / rate
            
            integral, error = quad(integrand, 0, X_required, 
                                  limit=100,
                                  epsrel=1e-6)
            
            # ПРЕОБРАЗОВАНИЕ В ОБЪЕМ РЕАКТОРА
            F_NH3_s = F_NH3 / 3600  # моль/с
            V_reactor = F_NH3_s * integral  # м³
            
            return V_reactor, X_required, error
            
        except Exception as e:
            return None, None, str(e)
    
    def calculate(self):
        """Основная функция расчета"""
        if self.calculating:
            return
            
        self.calculating = True
        
        try:
            # Получаем параметры
            T = self.temp_var.get()
            P = self.pressure_var.get()
            F = self.flow_var.get()
            NH3_0 = self.nh3_frac_var.get()
            target_H2 = self.target_h2_var.get()
            
            # Проверка входных данных
            if not all([500 <= T <= 800, 0.5 <= P <= 5.0, 21000 <= F <= 25000, 0.18 <= NH3_0 <= 0.22]):
                messagebox.showerror("Ошибка", "Параметры выходят за допустимые диапазоны")
                return
            
            # Расчет
            V_reactor, X_required, error = self.calculate_reactor_volume(T, P, F, NH3_0, target_H2)
            
            if V_reactor is None:
                messagebox.showerror("Ошибка", f"Ошибка расчета: {error}")
                return
            
            # Форматируем результаты
            results = f"""
=== РЕЗУЛЬТАТЫ РАСЧЕТА ===

Параметры процесса:
• Температура: {T:.1f} °C
• Давление: {P:.1f} атм
• Расход смеси: {F:.0f} м³/ч
• Доля NH₃: {NH3_0:.3f}
• Целевой H₂: {target_H2:.0f} м³/ч

Результаты:
• Степень превращения: {X_required:.3f}
• Объем реактора РИВ: {V_reactor:.3f} м³
• Ошибка расчета: {error:.2e}

Материальный баланс:
• Исходный NH₃: {NH3_0*100:.1f}%
• Конечный NH₃: {NH3_0*(1-X_required)*100:.1f}%
• Получено H₂: {X_required*100:.1f}% от теоретического

Рекомендации:
• Тип реактора: Идеальное вытеснение
• Режим: Изотермический
• Катализатор: Кобальт-силикагелевый
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results)
            
            # Обновляем графики
            self.update_plots_simple(T, P, F, NH3_0)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        finally:
            self.calculating = False
    
    def update_plots_simple(self, T, P, F, NH3_0):
        """Упрощенное обновление графиков"""
        try:
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
            
            T_kelvin = T + 273.15
            
            # График 1: Зависимость объема от температуры
            temps = np.linspace(500, 800, 10)
            volumes_temp = []
            for temp in temps:
                V, _, _ = self.calculate_reactor_volume(temp, P, F, NH3_0, 4800)
                volumes_temp.append(V if V else 0)
            
            self.ax1.plot(temps, volumes_temp, 'b-', linewidth=2)
            self.ax1.set_xlabel('Температура, °C', fontsize=self.font_size)
            self.ax1.set_ylabel('Объем реактора, м³', fontsize=self.font_size)
            self.ax1.set_title('Зависимость объема от температуры', fontsize=self.font_size)
            self.ax1.grid(True, alpha=0.3)
            
            # График 2: Зависимость объема от давления
            pressures = np.linspace(0.5, 5, 10)
            volumes_press = []
            for pressure in pressures:
                V, _, _ = self.calculate_reactor_volume(T, pressure, F, NH3_0, 4800)
                volumes_press.append(V if V else 0)
            
            self.ax2.plot(pressures, volumes_press, 'r-', linewidth=2)
            self.ax2.set_xlabel('Давление, атм', fontsize=self.font_size)
            self.ax2.set_ylabel('Объем реактора, м³', fontsize=self.font_size)
            self.ax2.set_title('Зависимость объема от давления', fontsize=self.font_size)
            self.ax2.grid(True, alpha=0.3)
            
            # График 3: Кинетика реакции
            X_range = np.linspace(0.01, 0.99, 50)
            rates = []
            for X in X_range:
                rate = self.reaction_rate(X, T_kelvin, P, NH3_0)
                rates.append(rate)
            
            self.ax3.plot(X_range, rates, 'purple', linewidth=2)
            self.ax3.set_xlabel('Степень превращения X', fontsize=self.font_size)
            self.ax3.set_ylabel('Скорость реакции, моль/(м³·с)', fontsize=self.font_size)
            self.ax3.set_title('Кинетика реакции разложения', fontsize=self.font_size)
            self.ax3.grid(True, alpha=0.3)
            
            # Скрываем четвертый график (зависимость объема от состава)
            self.ax4.axis('off')
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Ошибка при построении графиков: {e}")
    
    def test_composition_dependence(self):
        """Тестирование зависимости объема от состава"""
        test_params = {
            'T': 577,
            'P': 1.0,
            'F': 21500,
            'target_H2': 4800
        }
        
        results_text = "\n=== ТЕСТИРОВАНИЕ ЗАВИСИМОСТИ ОТ СОСТАВА ===\n\n"
        
        fractions = [0.18, 0.19, 0.20, 0.21, 0.22]
        results = []
        
        for frac in fractions:
            V, X, error = self.calculate_reactor_volume(
                test_params['T'], 
                test_params['P'], 
                test_params['F'], 
                frac, 
                test_params['target_H2']
            )
            if V is not None:
                results.append((frac, V, X))
                results_text += f"NH₃ = {frac:.3f} -> V = {V:.6f} м³, X = {X:.3f}\n"
        
        # Проверяем тренд
        if len(results) > 1:
            volumes = [r[1] for r in results]
            if volumes == sorted(volumes):
                results_text += "\n✗ Зависимость ВОЗРАСТАЮЩАЯ (ошибка!)\n"
            elif volumes == sorted(volumes, reverse=True):
                results_text += "\n✓ Зависимость УБЫВАЮЩАЯ (правильно!)\n"
            else:
                results_text += "\n? Нет четкого тренда\n"
        
        # Добавляем результаты в основное окно
        self.results_text.insert(tk.END, results_text)
    
    def clear_results(self):
        """Очистка результатов"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, "Результаты очищены.\nНажмите 'Рассчитать' для нового расчета.")

def main():
    root = tk.Tk()
    app = AmmoniaReactorCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()