library(tinytex)

# 带bib参考文献
pdflatex("mcmthesis-demo.tex", bib_engine = "biber") 

# 若不带big参考文献
# pdflatex("mcmthesis-demo.tex")

# 三线表
# 方法一: 适合简单表
library(xtable)
xtable(mtcars[1:10, 1:6]) |> 
  print(include.rownames = FALSE, booktabs = TRUE)

# 方法二: 适合复杂表
library(gt)
gt(mtcars[1:10, 1:6]) |> 
  as_latex() |> 
  cat()

