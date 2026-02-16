using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class MicroSecondToTimeCodeConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			TimeSpan timeSpan = TimeSpan.FromMilliseconds((double)(uint)value * 0.001);
			return $"{timeSpan.Minutes:00}:{timeSpan.Seconds:00}:{timeSpan.Milliseconds:000}";
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			uint num = uint.MaxValue;
			uint num2 = 0u;
			uint[] array = new uint[3] { 60000000u, 1000000u, 1000u };
			if (value != null)
			{
				string[] array2 = (value as string).Split(new char[1] { ':' });
				if (array2.Length <= array.Length)
				{
					num = 0u;
					string[] array3 = array2;
					foreach (string text in array3)
					{
						if (text.Length == 0)
						{
							num = uint.MaxValue;
							break;
						}
						num += uint.Parse(text) * array[num2++];
					}
				}
			}
			return num;
		}
	}
}
