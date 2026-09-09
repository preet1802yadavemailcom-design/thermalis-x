with open('ml/training/train_baseline_ladder.py', 'r', encoding='utf-8') as f:
    c = f.read()
# Replace any broken print with newline
c = c.replace('print("\n===', 'print("===')
c = c.replace('print(\"\n===', 'print("===')
with open('ml/training/train_baseline_ladder.py', 'w', encoding='utf-8') as f:
    f.write(c)

with open('ml/evaluation/ablation_study.py', 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = c2.replace('print("\n===', 'print("===')
c2 = c2.replace('print(\"\n===', 'print("===')
with open('ml/evaluation/ablation_study.py', 'w', encoding='utf-8') as f:
    f.write(c2)

print('Syntax fix complete.')
