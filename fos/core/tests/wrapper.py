#from __future__ import print_function

import os, sys

import subprocess

wrapper_original = r'''
\documentclass{article}
\usepackage{type1cm}
\renewcommand{\rmdefault}{pnc}
\usepackage{helvet}
\usepackage{courier}
\usepackage{textcomp}
\usepackage[papersize={72in,72in},body={70in,70in},margin={1in,1in}]{geometry}
\pagestyle{empty}
\begin{document}
\thispagestyle{empty}
\fontsize{16}{20}
'''

wrapper_new = r'''
\documentclass{article} 
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{bm}
\newcommand{\mx}[1]{\mathbf{\bm{#1}}} 
\newcommand{\vc}[1]{\mathbf{\bm{#1}}} 
\newcommand{\T}{\text{T}}             
\pagestyle{empty} 
\begin{document} 
'''

closing = r'''
\end{document}
'''

snippet = r'''
\sffamily \TeX rocks!!\\
\mbox{$\alpha\beta\gamma$}\\
$\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!
'''

document = wrapper_new + snippet + closing

label = "testfile"

latexfile = label+".tex"

dvifile = label+".dvi"

pngfile = "png/"+label+".png"

os.chdir(os.getcwd()+'/data')

latexfilehandle = open(latexfile, "w")

latexfilehandle.write(document)

latexfilehandle.close()

# compile LaTeX document. A DVI file is created

latex_process = subprocess.Popen(['latex -interaction=nonstopmode %s'  % latexfile], shell=True, cwd=os.getcwd())

latex_process.wait()

# Run dvipng on the generated DVI file. Use tight bounding box. 
# Magnification is set to 1200

#cmd_original = ["dvipng -o", "data/"+pngfile, "data/"+dvifile]

cmd_original = ["dvipng -o " + pngfile + ' ' + label]

print os.getcwd()

cmd_new = ["dvipng -q -T tight -x 1000 -z 1 -bg 'rgb 1 0.6 0.6' -o" + pngfile + ' ' + label]

print cmd_new

dvipng_process = subprocess.Popen(cmd_new, shell=True)

dvipng_process.wait()

eog_process = subprocess.Popen(['eog ' + pngfile], shell=True)

eog_process.wait()

# Remove temporary files
os.remove(label+'.tex')
os.remove(label+'.log')
os.remove(label+'.aux')
os.remove(label+'.dvi')

# but don't do it too soon!



