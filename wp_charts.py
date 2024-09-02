"""
@author: Ritalin
problem: Whatsapp konuşmalarının görselleştirilmesi
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# [1] Veri aktarma (Import the data)
Name = input("Listenizdeki kişinin adını giriniz:\n")
FilePath = f"C:\\Users\\bigfi\\OneDrive\\Belgeler\\wp-chats\\WhatsApp Chat with {Name}.txt"

with open(FilePath, "r", encoding="utf-8") as file:
    content = file.read()

# [2] Veri Temizleme (Data Cleaning)
content = content.splitlines()
content.pop(0) 

cleaned = []
temp_message = None
temp_person = None

for line in content:
    try:
        date_time, other = line.split(' - ', 1)
        date, time = date_time.split(', ', 1)

        if "<Media omitted>" in other:
            comment = "Media omitted"
            message = ""
        elif "<This message was edited>" in other:
            comment = "Message edited"
            message = temp_message if temp_message else "Message not found"
        else:
            person, message = other.split(': ', 1)
            comment = ""
            temp_message = message
            temp_person = person

        cleaned.append([date, time, temp_person, message, comment])

    except ValueError:
        pass 

df = pd.DataFrame(cleaned, columns=['Date', 'Time', 'Person', 'Message', 'Comment'])
df.drop('Comment', axis=1, inplace=True)
print(df['Message'].head())

# [3] Nitelik Mühendisliği (Feature Engineering)
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
df['Message Length'] = df['Message'].apply(len)
df['Weekday'] = df['Date'].dt.weekday  

# [4] Veri görselleştirme (Data Visualization)
fig, axes = plt.subplots(2, 2, figsize=(16, 9))  # 2 satır, 2 sütunluk subplot

# Kişiye göre mesaj gönderme sayısı
sns.countplot(data=df, x='Person', ax=axes[0, 0])
axes[0, 0].set_title("Kişiye göre mesaj gönderme sayısı", fontweight='bold')
axes[0, 0].set_xlabel(" ")
axes[0, 0].set_ylabel("Mesaj Sayısı")

# Yıllara göre mesaj gönderme sıklığı
df['Modified Date'] = df['Date'].apply(lambda x: x.replace(day=1))
sns.histplot(data=df, x='Date', ax=axes[0, 1], bins=25, color="gray")
axes[0, 1].set_title("Yıllara göre mesaj gönderme sıklığı", fontweight='bold')
axes[0, 1].set_ylabel("Mesaj Sayısı")
axes[0, 1].set_xlabel(" ")

# Günün hangi saatinde yazılmış?
df['Time Minutes'] = df['Time'].apply(lambda t: t.hour * 60 + t.minute)
ticks = range(0, 1441, 60)
labels = [f'{i // 60:02d}' for i in ticks]

sns.histplot(data=df, x='Time Minutes', hue='Person', bins=24, kde=False, palette='tab10', edgecolor='black', ax=axes[1, 0])
axes[1, 0].set_title("Gün İçinde Mesaj Gönderme Saatlerinin Dağılımı", fontweight='bold')
axes[1, 0].set_xlabel(" ")
axes[1, 0].set_ylabel("Mesaj Sayısı")
axes[1, 0].set_xticks(ticks)
axes[1, 0].set_xticklabels(labels)

# Hafta günlerine göre mesaj gönderme sıklığı
sns.countplot(data=df, x='Weekday', ax=axes[1, 1])
axes[1, 1].set_title("Hafta Günlerine Göre Mesaj Gönderme Sıklığı", fontweight='bold')
axes[1, 1].set_ylabel("Mesaj Sayısı")
axes[1, 1].set_xlabel(" ")
axes[1, 1].set_xticklabels(['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'])


# Kelime bulutu (Ayrı Grafik)
text = ' '.join(message for message in df['Message'])
additional_stopwords = {'de', 'da','ki', 'var', 'bu', 'ama', 'çok', 'benmi', 'bende', 
                        'deleted', 'https', 'mı', 'mi', 'null', 'message','this','was'
                        'www','feature','youtube','com','share','youtu','be','shorts'}

people = df['Person'].unique()
fig, axes = plt.subplots(len(people), 1, figsize=(8, 4 * len(people)))  # Adjust figsize as needed

for ax, person in zip(axes, people):
    person_messages = ' '.join(message for message in df[df['Person'] == person]['Message'])
    wordcloud = WordCloud(width=800, height=500, max_font_size=160, max_words=250, colormap="copper", background_color='white', stopwords=additional_stopwords).generate(person_messages)

    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(person, fontweight='bold')

plt.tight_layout()