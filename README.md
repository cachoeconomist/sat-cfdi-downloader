# 📈 Mexico Term Structure — Estructura Temporal de Tasas de Interés en México

> Réplica empírica del Capítulo 10 de **Campbell, Lo & MacKinlay (1997)** — *The Econometrics of Financial Markets* — con datos de deuda gubernamental mexicana (CETES, Bonos M y Udibonos), periodo 2010–2025.

---

## 📌 ¿De qué trata este proyecto?

Imagina que quieres saber si es buen momento para comprar un bono del gobierno, o si Banxico va a subir o bajar las tasas de interés. Una forma de responder es **mirar la "curva de rendimientos"** — una gráfica que relaciona el tiempo que prestas tu dinero (plazo) con la tasa de interés que recibes.

Este proyecto analiza los **bonos del gobierno mexicano** desde 2010 hasta 2025 para entender:

- ¿Qué forma tiene la curva de rendimientos en distintos momentos?
- ¿Qué nos dice esa forma sobre el futuro de la economía?
- ¿Podemos predecir las tasas de interés futuras con las actuales?

---

## 🗂️ Estructura del repositorio

```
mexico-term-structure/
├── data/
│   ├── raw/                  # Datos descargados directamente de Banxico (SIE)
│   └── processed/            # Datos limpios listos para análisis
│       ├── mexico_yields_clean.csv
│       ├── forward_rates.csv
│       ├── zero_coupon_curve.csv
│       └── nelson_siegel_curve.csv
├── outputs/
│   ├── figures/              # Gráficas generadas por cada notebook
│   └── tables/               # Tablas de resultados (CSV)
│       └── campbell_shiller_results.csv
├── 00_environment_setup.ipynb
├── 01_data_acquisition.ipynb
├── 02_discount_bonds.ipynb
├── 03_coupon_bonds.ipynb
├── 04_zero_coupon_curve.ipynb
├── 05_nelson_siegel.ipynb
├── 06_expectations_hypothesis.ipynb
├── 07_yield_spreads_forecasts.ipynb
├── 08_conclusion_results.ipynb
├── requirements.txt
└── README.md
```

---

## 🔧 Instrucciones de reproducción

```bash
# 1. Clonar el repositorio
git clone https://github.com/cachoeconomist/mexico-term-structure.git
cd mexico-term-structure

# 2. Crear entorno virtual
python3 -m venv venv && source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar los notebooks en orden
jupyter notebook
```

Ejecutar los notebooks en orden numérico, del `00` al `08`. El notebook `01` crea automáticamente los directorios `data/processed/`, `outputs/figures/` y `outputs/tables/` si no existen.

---

## 📊 Fuentes de datos

| Instrumento | Plazos | Fuente |
|-------------|--------|--------|
| **CETES** | 28, 91, 182, 364 días | Banco de México (SIE) |
| **Bonos M** | 3, 5, 10, 20, 30 años | Banco de México (SIE) |
| **Udibonos** | 3, 5, 10, 20, 30 años | Banco de México (SIE) |

- **Frecuencia:** Mensual
- **Periodo:** Enero 2010 – Diciembre 2025
- **Descarga:** 15 de mayo de 2026

---

## 📓 Descripción de los notebooks

### `00_environment_setup.ipynb`
Verificación del entorno Python. Comprueba que las librerías principales (`pandas`, `numpy`, `matplotlib`) estén instaladas correctamente.

---

### `01_data_acquisition.ipynb` — Adquisición y limpieza de datos
Descarga, limpieza y preparación de las series de rendimiento de CETES, Bonos M y Udibonos desde el SIE de Banxico. Incluye:
- Creación automática de directorios de salida.
- Verificación del mapeo de columnas de Udibonos.
- Transformación a log-rendimientos (ec. 10.1.3 de CLM).
- Generación de heatmaps de tasas para visualizar la evolución temporal.
- **Salida:** `data/processed/mexico_yields_clean.csv`

**Hallazgo clave:** Los CETES tienen datos completos; los Bonos M de 20 y 30 años presentan faltantes en algunos periodos (normal: no siempre hay bonos de muy largo plazo en el mercado); los Udibonos tienen muchos faltantes, especialmente el plazo de 5 años.

---

### `02_discount_bonds.ipynb` — CETES: bonos de descuento
Calcula precios implícitos, log-rendimientos y tasas forward para CETES. Sigue la Sección 10.1.1 de CLM.

**Corrección aplicada (v2):** Los precios de CETES se calculan con interés simple `P = 1/(1 + Y·d/360)`, que es la convención oficial de cotización en México (la versión original usaba interés compuesto, lo que era incorrecto).

**Hallazgo clave:** En enero 2023 (pico de tasas), las tasas forward eran más bajas que las tasas spot: el mercado anticipaba que Banxico bajaría las tasas. Eso es exactamente lo que ocurrió en 2024–2025.

**Marco teórico:**

$$P_{nt} = \frac{1}{(1 + Y_{nt})^n}, \qquad y_{nt} = -\frac{1}{n}\,p_{nt}, \qquad (1 + F_{nt}) = \frac{(1+Y_{n+1,t})^{n+1}}{(1+Y_{nt})^n}$$

---

### `03_coupon_bonds.ipynb` — Bonos M: duración y convexidad
Calcula duración de Macaulay, duración modificada y convexidad para los Bonos M. Sigue la Sección 10.1.2 de CLM.

**Corrección aplicada (v2):** Se usan los cupones reales de cada bono (`bonos_detalle.csv`) en lugar de aproximarlos con la tasa de rendimiento (YTM). Cuando el bono no cotiza a la par, la diferencia en duración puede ser de 0.3–0.5 años (el error era particularmente grande en 2023, cuando el cupón era ~7.5% pero el YTM ~10.4%).

**Hallazgo clave (enero 2023, tasas en su pico):**

| Plazo | Tasa (YTM) | Duración modificada | Caída ante +1% en tasas |
|-------|-----------|---------------------|--------------------------|
| 3 años | 9.94% | ~2.5 | −2.5% |
| 5 años | 8.76% | ~4.0 | −4.0% |
| 10 años | 8.69% | ~6.6 | −6.6% |
| 20 años | 8.71% | ~9.4 | **−9.4%** |

Los bonos de largo plazo son mucho más sensibles a los cambios en tasas. Si crees que Banxico va a bajar tasas, conviene comprar bonos largos (su precio subirá más). Si crees que las tasas subirán, es mejor evitar los bonos largos.

**Marco teórico:**

$$P_{cnt} = \sum_{i=1}^{n}\frac{C}{(1+Y_{cnt})^i} + \frac{1}{(1+Y_{cnt})^n}, \qquad D_{cnt} = \frac{\sum_{i=1}^{n}\frac{i\,C}{(1+Y_{cnt})^i} + \frac{n(1+C)}{(1+Y_{cnt})^n}}{P_{cnt}}, \qquad MD = \frac{D_{cnt}}{1+Y_{cnt}}$$

---

### `04_zero_coupon_curve.ipynb` — Curva cupón cero: spline de McCulloch
Estima la curva de rendimiento cupón cero mediante splines cúbicos (método de McCulloch 1971/1975). Sigue la Sección 10.1.3 de CLM (ec. 10.1.24–10.1.25).

**Corrección crítica aplicada (v2):** La versión original usaba optimización no lineal (`scipy.optimize.least_squares`) sobre los nodos del spline. El libro define el método de McCulloch como una **regresión OLS lineal** con funciones base `f_j(n)`. Se reemplazó completamente por la implementación OLS correcta.

**Hallazgo clave (diciembre 2025):** La función de descuento tiene forma convexa: cae rápido en plazos cortos (tasas cortas altas) y luego más lentamente en plazos largos (tasas largas más bajas). Esta forma es la firma de una curva ligeramente invertida que anticipa bajas de tasas.

**Marco teórico:**

$$P(n) = 1 + \sum_{j=1}^{J}a_j\,f_j(n), \qquad P_{cn} = P_1 C + P_2 C + \cdots + P_n(1+C)$$

---

### `05_nelson_siegel.ipynb` — Modelo Nelson-Siegel (Diebold-Li)
Estima la curva cupón cero con el modelo paramétrico de Nelson-Siegel (1987) en su versión dinámica de Diebold-Li (2006). Complementa el spline con una representación de solo 4 parámetros.

**Parámetros estimados para enero 2023 (pico de tasas):**

| Componente | Valor | Interpretación |
|------------|-------|----------------|
| Nivel (β₀) | 8.27% | Tasa de muy largo plazo esperada por el mercado |
| Pendiente (β₁) | 2.01% | Inclinación de la curva; positivo = curva normal |
| Curvatura (β₂) | −1.43% | Giba en la parte media de la curva |
| Decaimiento (λ) | 1.75 | Los efectos de corto plazo desaparecen hacia los 5 años |

**Salida:** `data/processed/nelson_siegel_curve.csv`

**Marco teórico:**

$$y(\tau) = \beta_0 + \beta_1\left(\frac{1-e^{-\lambda\tau}}{\lambda\tau}\right) + \beta_2\left(\frac{1-e^{-\lambda\tau}}{\lambda\tau} - e^{-\lambda\tau}\right)$$

---

### `06_expectations_hypothesis.ipynb` — Hipótesis de Expectativas (CETES)
Prueba la Hipótesis de Expectativas Pura (PEH) en el mercado de CETES usando regresiones forward-spot. Sigue la Sección 10.2.1 de CLM (ec. 10.2.9–10.2.11).

**Resultados:**

| Transición | β (ideal = 1) | R² | Interpretación |
|------------|---------------|----|----------------|
| 28 → 91 días | 0.974 | ~0.88 | Pequeña prima de liquidez |
| 91 → 182 días | 0.981 | ~0.92 | ✅ EH se cumple bien |
| 182 → 364 días | 0.961 | ~0.91 | ✅ EH se cumple bien |

**Conclusión:** Para plazos de 3 a 6 meses, las tasas forward de CETES son **excelentes predictores** de las tasas futuras (R² > 0.90). Para el plazo más corto (28 → 91 días), los inversionistas exigen una pequeña prima de liquidez adicional.

---

### `07_yield_spreads_forecasts.ipynb` — Regresiones de Campbell-Shiller
Replica las regresiones de Campbell & Shiller (1991) para evaluar la Hipótesis de Expectativas usando el spread de rendimiento entre Bonos M y CETES. Sigue las ecuaciones 10.2.16 y 10.2.18 de CLM.

**Corrección aplicada (v2):** Se eliminó la lectura de `nelson_siegel_curve.csv` que la versión original intentaba cargar pero que no era necesaria para las regresiones, evitando un error de archivo no encontrado.

**Especificación econométrica:**

$$y_{n-1,t+1} - y_{n,t} = \alpha_n + \beta_n\,\frac{s_{n,t}}{n-1} + \epsilon_{n,t} \qquad \text{(ec. 10.2.16, EH: }\beta_n=1\text{)}$$

$$s_{n,t}^* = \mu_n + \gamma_n\,s_{n,t} + \nu_{n,t}, \qquad s_{n,t}^* = \sum_{i=1}^{n-1}\left(1-\frac{i}{n}\right)\Delta y_{1,t+i} \qquad \text{(ec. 10.2.18, EH: }\gamma_n=1\text{)}$$

**Resultados β (predecir cambios en tasa larga):**

| Plazo | β | ¿La EH se cumple? |
|-------|---|-------------------|
| 3 años | 0.14 | ❌ No |
| 5 años | 0.20 | ❌ No |
| 10 años | 0.29 | ❌ No |
| 20 años | 0.48 | ❌ No |
| 30 años | −0.01 | ❌ No |

**Resultados γ (predecir cambios en tasa corta):**

| Plazo | γ | Interpretación |
|-------|---|----------------|
| 3 años | 0.04 | Solo el 4% del spread se traduce en cambios de tasa corta |
| 5 años | 0.06 | Solo el 6% |
| 10 años | 0.09 | Solo el 9% |
| 20 años | 0.21 | 21% |
| 30 años | 0.33 | 33% |

**Salidas:** `outputs/tables/campbell_shiller_results.csv`, `outputs/figures/campbell_shiller_coefficients.png`

---

### `08_conclusion_results.ipynb` — Conclusiones y resultados consolidados
Integra los resultados de todos los notebooks, replica los cuadros de CLM con datos mexicanos y genera las visualizaciones finales.

**Errores corregidos (v2):** Se corrigieron rutas de archivos que usaban paths absolutos del entorno local del autor (incompatibles con otras máquinas), reemplazándolos por paths relativos al directorio del proyecto.

---

## 🔍 Resultados principales

### Comparación con Estados Unidos (Tabla 10.3 del libro)

| Aspecto | EE.UU. 1952–1991 (CLM) | México 2010–2025 (este estudio) |
|---------|------------------------|----------------------------------|
| β para bonos largos (20 años) | −2.26 | ~0.48 (cercano a cero) |
| γ para bonos largos (20 años) | 0.44 | 0.21 |
| R² en regresiones β | Bajos (pero significativos) | Muy bajos (<11%) |
| EH en plazos cortos (≤6 meses) | Parcialmente | ✅ Mejor que en EE.UU. (R² > 0.90) |

**¿Por qué las diferencias?** El mercado mexicano de bonos largos es menos líquido y está más influido por factores externos (tasas de la Fed, aversión al riesgo global). La política monetaria de Banxico tiene un impacto más directo en el extremo corto de la curva que en el extremo largo.

---

## 🧠 Conclusiones finales

1. **La hipótesis de expectativas funciona bien en México para plazos de 3 a 6 meses.** Las tasas forward de CETES predicen excelentemente las tasas futuras (R² > 0.90). Si quieres saber hacia dónde van las tasas en los próximos 3–6 meses, mira las tasas forward de CETES.

2. **Para plazos más largos (3–30 años), la hipótesis no se cumple.** El spread no predice movimientos de tasas largas, y solo una pequeña fracción del spread se traduce en cambios de tasas cortas. Los β son todos negativos (como en EE.UU.), lo que indica que un spread positivo alto se asocia a caídas futuras de la tasa larga.

3. **La mayor parte del spread refleja "primas de plazo"** (compensación por riesgo de inflación, liquidez e incertidumbre), no expectativas de tasas futuras. Más del 67% del spread a largo plazo es prima de plazo, no información sobre tasas futuras.

4. **En enero 2023 (pico de tasas), la curva estaba invertida.** Tanto los splines cúbicos como el modelo Nelson-Siegel capturaron que el mercado anticipaba bajas de tasas — que efectivamente ocurrieron en 2024–2025.

5. **La duración mide el riesgo de tasa de interés.** Un bono a 20 años puede caer ~9.4% si las tasas suben 1%. Esto es crucial para inversores y administradores de fondos de deuda.

6. **El mercado mexicano de deuda es eficiente en el corto plazo** (CETES), pero en el largo plazo está más dominado por factores globales (Fed, aversión al riesgo) que por la política monetaria de Banxico.

---

## 📊 Conceptos básicos

| Término | ¿Qué significa? |
|---------|-----------------|
| **CETES** | Bonos del gobierno a corto plazo (1 mes a 1 año). Se venden con descuento: compras hoy por menos del valor nominal. |
| **Bonos M** | Bonos a largo plazo con cupón (3 a 30 años). Pagan intereses periódicos más el principal al vencimiento. |
| **Udibonos** | Bonos indexados a la inflación (UDIS). Protegen el poder adquisitivo. |
| **Curva de rendimientos** | Gráfica que muestra la tasa de interés según el plazo. |
| **Curva normal** | Tasas cortas < tasas largas. Señal de economía saludable. |
| **Curva invertida** | Tasas cortas > tasas largas. Suele anticipar una recesión o bajadas de tasas. |
| **Duración** | Mide qué tanto cambia el precio de un bono ante variaciones en tasas. Mayor duración = mayor riesgo. |
| **Tasa forward** | Tasa de interés implícita para un periodo futuro, calculada con las tasas spot actuales. |
| **Hipótesis de expectativas** | Teoría que dice que las tasas forward son predictores óptimos de las tasas spot futuras. |
| **Prima de plazo** | Compensación extra exigida por los inversionistas por prestar a largo plazo. |
| **Spread** | Diferencia entre la tasa larga y la tasa corta, snt = ynt − y1t. |

---

## 📚 Bibliografía

- Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). *The Econometrics of Financial Markets*. Princeton University Press. Capítulo 10.
- Nelson, C. R., & Siegel, A. F. (1987). Parsimonious modeling of yield curves. *Journal of Business*, 60(4), 473–489.
- Diebold, F. X., & Li, C. (2006). Forecasting the term structure of government bond yields. *Journal of Econometrics*, 130(2), 337–364.
- McCulloch, J. H. (1975). The tax-adjusted yield curve. *Journal of Finance*, 30(3), 811–830.
- Campbell, J. Y., & Shiller, R. J. (1991). Yield spreads and interest rate movements: a bird's eye view. *Review of Economic Studies*, 58(3), 495–514.
- **Datos:** Banco de México, Sistema de Información Económica (SIE), 2010–2025.

---

*Última actualización: Mayo 2026*
