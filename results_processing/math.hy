(import [pandas :as pd]
        math)

(setv dataset (pd.read_csv "game_stats.csv"))
(setv time (get dataset "time"))
(setv score (get dataset "score"))

(defn to_square[num]
 (* num num))

(defn get_math_expectation[column]
  (/ (column.sum) (len column))) 

(defn get_dispersion[column]
  ( - (get_math_expectation (column.map to_square)) (math.pow (get_math_expectation column) 2)))
  
(print "Time Math Expectation:" (get_math_expectation time))
(print "Score Dispersion:" (get_dispersion score))