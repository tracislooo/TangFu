$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
public static class CircleProgressVariants {
 public static void Build(string input,string output) {
  Directory.CreateDirectory(output);
  using(var src=new Bitmap(input))
  using(var preview=new Bitmap(680,910))
  using(var g=Graphics.FromImage(preview))
  using(var font=new Font("Arial",12)) {
   if(src.Width!=196 || src.Height!=19) throw new Exception("Unexpected size");
   // Same effective horizontal bounds as the previous progress bar, x=6..188.
   // The 10-pixel circle has left x=6 at 0% and x=179 at 100%.
   int originalCount=0;
   for(int y=0;y<19;y++) for(int x=0;x<196;x++) if(src.GetPixel(x,y).A>0) originalCount++;
   g.Clear(Color.FromArgb(238,240,244));
   g.DrawString("Circle position | Transparent PNG | 196 x 19 px",font,Brushes.Black,12,12);
   string report="segment,percent,canvas_width,canvas_height,circle_left_x,circle_center_x,shift_x,verified_circle_pixels\r\n";
   for(int n=1;n<=19;n++) {
    int left=6+(int)Math.Round(173*n/20.0,MidpointRounding.AwayFromZero);
    int shift=left-179;
    using(var dst=new Bitmap(196,19,PixelFormat.Format32bppArgb)) {
     for(int y=0;y<19;y++) for(int x=0;x<196;x++) {
      var c=src.GetPixel(x,y);
      if(c.A>0) dst.SetPixel(x+shift,y,c);
     }
     string path=Path.Combine(output,String.Format("circle_{0:00}_of_20_{1:00}percent.png",n,n*5));
     dst.Save(path,ImageFormat.Png);
     using(var saved=new Bitmap(path)) {
      if(saved.Width!=196 || saved.Height!=19 || !Image.IsAlphaPixelFormat(saved.PixelFormat)) throw new Exception("Format mismatch");
      int count=0;
      for(int y=0;y<19;y++) for(int x=0;x<196;x++) {
       var c=saved.GetPixel(x,y);
       int ox=x-shift;
       int expected=ox>=0 && ox<196 ? src.GetPixel(ox,y).A : 0;
       if(c.A!=expected) throw new Exception("Translation or transparency mismatch");
       if(c.A>0) {
        if(c.ToArgb()!=src.GetPixel(ox,y).ToArgb()) throw new Exception("Circle pixel changed");
        count++;
       }
      }
      if(count!=originalCount) throw new Exception("Circle clipped");
      report+=String.Format("{0},{1},196,19,{2},{3},{4},{5}\r\n",n,n*5,left,left+4.5,shift,count);
     }
     int py=44+(n-1)*44;
     g.DrawString(String.Format("{0:00}/20 {1:00}%",n,n*5),font,Brushes.Black,14,py+4);
     for(int yy=0;yy<5;yy++) for(int xx=0;xx<49;xx++) {
      using(var brush=new SolidBrush((xx+yy)%2==0?Color.White:Color.FromArgb(213,216,222)))
       g.FillRectangle(brush,140+xx*8,py+yy*8,8,8);
     }
     g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
     g.PixelOffsetMode=System.Drawing.Drawing2D.PixelOffsetMode.Half;
     g.DrawImage(dst,new Rectangle(140,py+2,392,38),0,0,196,19,GraphicsUnit.Pixel);
    }
   }
   preview.Save(Path.Combine(output,"preview.png"),ImageFormat.Png);
   File.WriteAllText(Path.Combine(output,"verification.csv"),report);
   File.WriteAllText(Path.Combine(output,"README.txt"),"19 transparent PNG images, 5%-95%, fixed 196x19 canvas.\r\nOnly the original circle is translated horizontally; its RGBA pixels, size and vertical position are unchanged.\r\nTravel bounds follow the previous bar: outer x=6..188. At 0%, circle left=6; at 100%, original circle left=179.\r\nEach intermediate position is rounded to nearest pixel.\r\n");
  }
 }
}
'@ -ReferencedAssemblies System.Drawing
[CircleProgressVariants]::Build('C:\Users\traci\AppData\Local\Temp\codex-clipboard-7c210798-bdc7-4e45-acc8-48cab0c7a32b.png','G:\Doc\ChatGPT\New project\圆圈进度条-透明PNG-1至19段')
