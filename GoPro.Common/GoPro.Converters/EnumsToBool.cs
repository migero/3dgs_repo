using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class EnumsToBool : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			if (parameter != null && (Type)parameter != values[0].GetType())
			{
				return false;
			}
			int num = (int)values[0];
			for (int i = 1; i < values.Length; i++)
			{
				if (num == (int)values[i])
				{
					return true;
				}
			}
			return false;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
